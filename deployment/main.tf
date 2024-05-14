resource "scaleway_instance_ip" "main" {
  type = "routed_ipv4"
}

resource "scaleway_instance_security_group" "main" {
  inbound_default_policy  = "drop"
  outbound_default_policy = "accept"
  stateful                = true

  inbound_rule {
    action = "accept"
    port   = 22
  }
  inbound_rule {
    action = "accept"
    port   = 80
  }
  inbound_rule {
    action = "accept"
    port   = 443
  }
}

resource "scaleway_instance_server" "main" {
  type              = var.scaleway_instance_type
  image             = "docker"
  ip_id             = scaleway_instance_ip.main.id
  routed_ip_enabled = true
  security_group_id = scaleway_instance_security_group.main.id

  root_volume {
    delete_on_termination = false
  }
}

data "scaleway_account_project" "main" {
  project_id = var.scaleway_project_id
}

data "scaleway_iam_group" "deployers" {
  organization_id = data.scaleway_account_project.main.organization_id
  name            = "terraform-deployers"
}

locals {
  openmetadata_hostname = "openmetadata.${var.dns_zone}"

  work_dir = "/root/datacube"
}

resource "scaleway_domain_record" "dns" {
  for_each = toset([local.openmetadata_hostname])

  dns_zone = var.dns_zone
  name     = replace(each.key, ".${var.dns_zone}", "")
  type     = "A"
  data     = scaleway_instance_server.main.public_ip
  ttl      = 60
}

resource "null_resource" "up" {
  triggers = {
    always_run = timestamp()
  }

  connection {
    type        = "ssh"
    user        = "root"
    host        = scaleway_instance_server.main.public_ip
    private_key = var.ssh_private_key
  }

  provisioner "remote-exec" {
    inline = [
      "rm -rf ${local.work_dir}",
      "mkdir -p ${local.work_dir}",
    ]
  }

  provisioner "file" {
    content = sensitive(<<-EOT
    STACK_VERSION=${var.stack_version}
    OPENMETADATA_HOSTNAME=${local.openmetadata_hostname}

    DB_PARAMS='useSSL=true&serverTimezone=UTC'
    DB_USER=${var.db_user}
    DB_USER_PASSWORD=${var.db_user_password}
    DB_HOST=${var.db_host}
    DB_PORT=${var.db_port}
    OM_DATABASE=${var.om_database}

    AIRFLOW_DB=${var.om_database}
    AIRFLOW_DB_PARAMS='useSSL=true&serverTimezone=UTC'
    AIRFLOW_DB_USER=${var.db_user}
    AIRFLOW_DB_PASSWORD=${var.db_user_password}
    AIRFLOW_DB_HOST=${var.db_host}
    AIRFLOW_DB_PORT=${var.db_port}

    EOT
    )
    destination = "${local.work_dir}/.env"
  }

  provisioner "file" {
    source      = "${path.root}/docker-compose.yml"
    destination = "${local.work_dir}/docker-compose.yml"
  }

  provisioner "file" {
    content     = var.ssh_tunnel_key
    destination = "/tmp/tunnel.key"
  }

  provisioner "remote-exec" {
    inline = [
      "docker network prune --force",
      "docker image prune --all --force --filter 'until=168h'",
      "docker container prune --force --filter 'until=168h'",
      "cd ${local.work_dir}",
      "docker compose --progress=plain up --pull=always --force-recreate --remove-orphans --wait --wait-timeout 1200 --quiet-pull --detach",
    ]
  }
}

provider "system" {
  ssh {
    user        = "root"
    host        = scaleway_instance_server.main.public_ip
    private_key = var.ssh_private_key
  }
}

resource "system_file" "dora_db_tunnel" {
  path    = "/etc/systemd/system/dora-db-tunnel.service"
  mode    = 644
  user    = "root"
  group   = "root"
  content = <<EOT
[Unit]
Description=DORA DB tunnel
After=network.target

[Service]
Restart=always
RestartSec=60
ExecStartPre=+/bin/chmod 600 /tmp/tunnel.key
ExecStart=/bin/ssh -N -L 172.17.0.1:10000:${var.dora_db_host}:${var.dora_db_port} -i /tmp/tunnel.key git@ssh.osc-secnum-fr1.scalingo.com

[Install]
WantedBy=multi-user.target
EOT
}

resource "system_service_systemd" "dora_db_tunnel" {
  name    = trimsuffix(system_file.dora_db_tunnel.basename, ".service")
  enabled = true
  status  = "started"
}

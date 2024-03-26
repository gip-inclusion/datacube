
variable "dns_subdomain" {
  description = "DNS subdomain where the public hostnames will be created within dns_zone (optional)"
  type        = string
  default     = ""
}

variable "dns_zone" {
  description = "DNS zone where the public hostnames will be created"
  type        = string
}

variable "environment" {
  description = "Identifier of the target environment"
  type        = string
}

variable "scaleway_access_key" {
  description = "Scaleway access key (https://console.scaleway.com/iam/api-keys)"
  type        = string
  sensitive   = true
}

variable "scaleway_application_id" {
  description = "ID of the application owning the api keys"
  type        = string
}

variable "scaleway_secret_key" {
  description = "Scaleway secret key (https://console.scaleway.com/iam/api-keys)"
  type        = string
  sensitive   = true
}

variable "scaleway_project_id" {
  description = "Scaleway project id (https://console.scaleway.com/project/settings)"
  type        = string
}

variable "scaleway_instance_type" {
  description = "Scaleway instance type (ex. GP1-XS, see https://www.scaleway.com/en/pricing/?tags=compute)"
  type        = string
  default     = "GP1-XS"
}

variable "ssh_private_key" {
  description = "The associated public key will be deployed to the instance"
  type        = string
  sensitive   = true
}

variable "stack_version" {
  description = "Version (e.g. sha or semver) of the stack services to deploy"
  type        = string
}

variable "db_user" {
  description = "The user associated with the database for openmetadata server and its ingester"
  type        = string
  sensitive   = true
}

variable "db_user_password" {
  description = "The password associated with the database for openmetadata server and its ingester"
  type        = string
  sensitive   = true
}

variable "db_host" {
  description = "The host associated with the database for openmetadata server and its ingester"
  type        = string
  sensitive   = true
}

variable "db_port" {
  description = "The port associated with the database for openmetadata server and its ingester"
  type        = string
  sensitive   = true
}

variable "om_database" {
  description = "The database name associated with the database for openmetadata server and its ingester"
  type        = string
  sensitive   = true
}

variable "openmetadata_hostname" {
  description = "The hostname for the Openmetadata server"
  type        = string
}

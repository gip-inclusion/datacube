# deployment

## Howto
Install [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
on your system.

## Prérequis Scaleway

* Une organisation au top-level pour gérer les projets, ici c'est `GIP Plateforme de l'Inclusion`.
* Un projet `datacube` qui contiendra les ressources métier (machines, DNS, buckets, ...)
* Un projet `terraform-states` partagé qui contient les states terraform.
* Un bucket `datacube-tf-states` dans le projet `terraform-states` pour recevoir les états de déploiement.

> **Attention**: Les buckets Scaleway sont uniques sur toute leur plateforme; il faut donc choisir leur nom avec précaution.

Du côté IAM:

* Un groupe `terraform-editors` qui a tous les droits sur les Object Storage du projet `terraform-states`, ET les droits suivants:
  - la permission `IAMReadOnly` sur l'organisation
  - la permission `ProjectReadOnly` sur l'organisation
* Un groupe `datacube-admins` qui a tous les droits sur le projet `datacube`
* Une application `datacube-deploy` qui est dans les deux groupes et peut donc à la fois écrire les states Terraform et créer des ressources projet.

Cette application aura besoin d'une API Key (à créer également) pour accéder aux Object Storage de `terraform-states`, à définir en "projet préféré".

Cette API Key se compose d'une `ACCESS_KEY` et `SECRET_KEY`.

Enfin, il faudra générer une clé SSH pour le service:

```bash
ssh-keygen -t ed25519 -C <ENVIRONMENT> -f /tmp/datacube.key -N ''
```

et l'uploader côté Scalingo pour permettre de créer un tunnel SSH vers les bases de données des produits hébergées sur Scalingo.


## Provisioning
Vous aurez besoin de remplir les variables terraform.

```bash
cp template.terraform.tfvars.json terraform.tfvars.json
vim terraform.tfvars.json
```

Puis il faudra exécuter le plan:

```bash
terraform init -backend-config "bucket=datacube-tf-states" -backend-config "key=openmetdata" \
    -backend-config "access_key=<ACCESS_KEY>" -backend-config "secret_key=<SECRET_KEY>"

terraform plan

terraform apply
```

## OpenMetadata
Les ingesters OpenMetadata ont besoin de se connecter à des bases de données distantes.

A cette fin:
- une flexible IP spéciale est autorisée pour accéder à la base de données des Emplois (via le support Clever Cloud).
- des tunnels SSH sont effectués vers les instances Scalingo via la clé `datacube.key`

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  project_name = "constructure"
  environment  = var.environment
}

module "network" {
  source = "./modules/network"

  project_name = local.project_name
  environment  = local.environment
}

module "storage" {
  source = "./modules/storage"

  project_name = local.project_name
  environment  = local.environment
}

module "database" {
  source = "./modules/database"

  project_name      = local.project_name
  environment       = local.environment
  vpc_id            = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
}

module "compute" {
  source = "./modules/compute"

  project_name        = local.project_name
  environment         = local.environment
  vpc_id              = module.network.vpc_id
  public_subnet_ids   = module.network.public_subnet_ids
  private_subnet_ids  = module.network.private_subnet_ids
  db_security_group_id = module.database.db_security_group_id
  s3_bucket_name      = module.storage.bucket_name
}


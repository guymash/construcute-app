variable "project_name" {
  description = "Base project name"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for ALB"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS tasks"
  type        = list(string)
}

variable "db_security_group_id" {
  description = "Security group ID for DB to allow from ECS if needed"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 bucket for media"
  type        = string
}


# ── General ────────────────────────────────────────────────────
variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  description = "Project name used as prefix for resource naming"
  type        = string
  default     = "joblens"
}

# ── RDS (PostgreSQL) ──────────────────────────────────────────
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "joblens"
}

variable "db_username" {
  description = "Master username for RDS"
  type        = string
  default     = "joblens_admin"
}

variable "db_password" {
  description = "Master password for RDS (set via tfvars or env)"
  type        = string
  sensitive   = true
}

variable "db_allocated_storage" {
  description = "Allocated storage in GB for RDS"
  type        = number
  default     = 20
}

# ── OpenSearch ────────────────────────────────────────────────
variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = "t3.small.search"
}

variable "opensearch_volume_size" {
  description = "EBS volume size in GB for OpenSearch"
  type        = number
  default     = 20
}

# ── ElastiCache (Redis) ──────────────────────────────────────
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

# ── ECS Fargate ──────────────────────────────────────────────
variable "ecs_api_cpu" {
  description = "CPU units for ECS API task (1024 = 1 vCPU)"
  type        = number
  default     = 256
}

variable "ecs_api_memory" {
  description = "Memory in MiB for ECS API task"
  type        = number
  default     = 512
}

variable "ecs_worker_cpu" {
  description = "CPU units for ECS Celery worker task"
  type        = number
  default     = 256
}

variable "ecs_worker_memory" {
  description = "Memory in MiB for ECS Celery worker task"
  type        = number
  default     = 512
}

variable "api_desired_count" {
  description = "Desired number of API tasks"
  type        = number
  default     = 1
}

variable "worker_desired_count" {
  description = "Desired number of Celery worker tasks"
  type        = number
  default     = 1
}

# ── Domain ───────────────────────────────────────────────────
variable "domain_name" {
  description = "Root domain name (e.g., joblens.in)"
  type        = string
  default     = ""
}

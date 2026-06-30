variable "name" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" {
  type        = list(string)
  description = "Private subnets for the tasks."
}
variable "service_security_group_id" {
  type        = string
  description = "SG for the tasks (created in composition; allows ALB ingress, DB egress)."
}
variable "target_group_arn" { type = string }

variable "image" {
  type        = string
  description = "Full container image reference (ECR url:tag)."
}

variable "app_port" {
  type    = number
  default = 8000
}
variable "cpu" {
  type    = number
  default = 256
}
variable "memory" {
  type    = number
  default = 512
}
variable "desired_count" {
  type    = number
  default = 1
}

variable "environment" {
  type        = list(object({ name = string, value = string }))
  default     = []
  description = "Plain environment variables for the container."
}

variable "secrets" {
  type        = list(object({ name = string, valueFrom = string }))
  default     = []
  description = "Secrets injected as env vars (valueFrom = Secrets Manager ARN)."
}

variable "secret_arns" {
  type        = list(string)
  default     = []
  description = "ARNs the execution role may read (must cover everything in `secrets`)."
}

variable "log_retention_days" {
  type    = number
  default = 14
}
variable "container_insights" {
  type    = bool
  default = false
}

variable "listener_dependency" {
  type        = any
  default     = null
  description = "Pass the ALB listener(s) so the service is created after them."
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "name" { type = string }
variable "vpc_id" { type = string }
variable "public_subnet_ids" { type = list(string) }

variable "app_port" {
  type    = number
  default = 8000
}

variable "health_check_path" {
  type    = string
  default = "/health"
}

variable "certificate_arn" {
  type        = string
  default     = ""
  description = "ACM cert ARN for HTTPS. Empty = HTTP only (dev)."
}

variable "tags" {
  type    = map(string)
  default = {}
}

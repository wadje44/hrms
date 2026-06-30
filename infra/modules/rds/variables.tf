variable "name" { type = string }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "app_security_group_id" {
  type        = string
  description = "Security group of the ECS service allowed to reach the DB."
}

variable "db_name" {
  type    = string
  default = "hrms"
}
variable "db_username" {
  type    = string
  default = "hrms"
}
variable "db_password" {
  type      = string
  sensitive = true
}

variable "engine_version" {
  type    = string
  default = "16.4"
}
variable "instance_class" {
  type    = string
  default = "db.t4g.micro"
}
variable "allocated_storage" {
  type    = number
  default = 20
}
variable "max_allocated_storage" {
  type    = number
  default = 50
}
variable "multi_az" {
  type    = bool
  default = false
}
variable "backup_retention_period" {
  type    = number
  default = 1
}
variable "deletion_protection" {
  type    = bool
  default = false
}
variable "skip_final_snapshot" {
  type    = bool
  default = true
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "name" {
  type    = string
  default = "hrms-dev"
}

variable "image_tag" {
  type        = string
  default     = "latest"
  description = "ECR image tag the ECS task runs. CI overrides this per deploy."
}

variable "site_bucket_name" {
  type        = string
  description = "Globally-unique S3 bucket name for the SPA."
}

variable "github_repo" {
  type        = string
  description = "owner/repo for GitHub Actions OIDC, e.g. wadje44/hrms"
}

variable "create_oidc_provider" {
  type        = bool
  default     = true
  description = "Set false if a GitHub OIDC provider already exists in the account."
}

variable "desired_count" {
  type    = number
  default = 1
}

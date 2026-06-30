variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "aws_profile" {
  type        = string
  default     = ""
  description = "AWS CLI profile to deploy with. Empty = use ambient credentials/AWS_PROFILE. Set per account to switch targets."
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

variable "cheap_mode" {
  type        = bool
  default     = true
  description = "Cost-optimized demo mode: no NAT gateway, run the API task in public subnets behind the ALB security group. Saves ~$32/mo. Set false for a NAT-isolated setup."
}

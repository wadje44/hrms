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
  default = "hrms-prod"
}

variable "image_tag" {
  type        = string
  default     = "latest"
  description = "ECR image tag the ECS task runs. CI overrides this per deploy."
}

variable "site_bucket_name" {
  type = string
}

variable "github_repo" {
  type = string
}

variable "create_oidc_provider" {
  type    = bool
  default = false # usually already created by the dev stack in the same account
}

variable "desired_count" {
  type    = number
  default = 2
}

variable "alb_certificate_arn" {
  type        = string
  default     = ""
  description = "ACM cert (in var.region) for the ALB HTTPS listener."
}

variable "cloudfront_certificate_arn" {
  type        = string
  default     = ""
  description = "ACM cert (us-east-1) for the CloudFront custom domain."
}

variable "frontend_aliases" {
  type    = list(string)
  default = []
}

variable "db_snapshot_identifier" {
  type        = string
  default     = ""
  description = "Restore the database from this snapshot ID (used on a fresh apply). Empty = new empty DB. See docs/DATABASE-RESTORE.md."
}

variable "name" { type = string }

variable "github_repo" {
  type        = string
  description = "owner/repo, e.g. wadje44/hrms"
}

variable "github_refs" {
  type        = list(string)
  default     = ["ref:refs/heads/main"]
  description = "Subject patterns allowed to assume the role (branches/tags/environments)."
}

variable "create_oidc_provider" {
  type        = bool
  default     = true
  description = "Set false if the GitHub OIDC provider already exists in the account."
}

variable "existing_oidc_provider_arn" {
  type    = string
  default = ""
}

variable "ecr_repository_arn" { type = string }
variable "site_bucket_arn" { type = string }

variable "pass_role_arns" {
  type        = list(string)
  default     = []
  description = "Task execution/role ARNs CI may pass when registering task defs."
}

variable "tags" {
  type    = map(string)
  default = {}
}

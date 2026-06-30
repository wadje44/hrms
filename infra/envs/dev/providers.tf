provider "aws" {
  region = var.region
  # Pick the AWS account purely via this profile (or leave empty to use the
  # ambient AWS_PROFILE / env credentials). Switching accounts = change this.
  profile = var.aws_profile != "" ? var.aws_profile : null

  default_tags {
    tags = {
      Project = "prabha-hrms"
      Env     = "dev"
      Managed = "terraform"
    }
  }
}

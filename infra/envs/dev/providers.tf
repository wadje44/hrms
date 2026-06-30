provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project = "prabha-hrms"
      Env     = "dev"
      Managed = "terraform"
    }
  }
}

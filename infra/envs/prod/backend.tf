# Remote state for prod. Fill in and `terraform init` (see infra/README.md).
terraform {
  backend "s3" {
    # bucket         = "my-hrms-tfstate"
    # key            = "prod/terraform.tfstate"
    # region         = "ap-south-1"
    # dynamodb_table = "hrms-tf-locks"
    # encrypt        = true
  }
}

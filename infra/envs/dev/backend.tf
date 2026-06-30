# Remote state. Fill in the bucket/table you bootstrapped (see infra/README.md),
# then run `terraform init`. Kept as a partial config so values can also be
# supplied via `terraform init -backend-config=...`.
terraform {
  backend "s3" {
    # bucket         = "my-hrms-tfstate"
    # key            = "dev/terraform.tfstate"
    # region         = "ap-south-1"
    # dynamodb_table = "hrms-tf-locks"
    # encrypt        = true
  }
}

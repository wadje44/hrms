# Infrastructure (Terraform)

Provisions the Prabha HRMS stack on AWS:

```
Route53/ACM ─ CloudFront ─ S3 (React SPA)
                              │
                          ALB (HTTPS) ─ ECS Fargate (FastAPI) ─ RDS Postgres (private)
                                              │
                                    Secrets Manager (DB password, JWT secret)
                                    ECR (api image) · CloudWatch Logs
```

## Layout

- `modules/` — reusable building blocks (network, ecr, rds, alb, ecs, secrets, frontend, iam_oidc)
- `envs/dev`, `envs/prod` — per-environment compositions
- `backend.tf` (per env) — S3 remote state + DynamoDB lock

## Bootstrapping remote state (one-time, per account)

The S3 bucket + DynamoDB table that hold Terraform state must exist before
`terraform init`. Create them once (replace names), then fill `backend.tf`:

```bash
aws s3api create-bucket --bucket my-hrms-tfstate --region ap-south-1 \
  --create-bucket-configuration LocationConstraint=ap-south-1
aws s3api put-bucket-versioning --bucket my-hrms-tfstate \
  --versioning-configuration Status=Enabled
aws dynamodb create-table --table-name hrms-tf-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST
```

## Usage

```bash
cd envs/dev
terraform init
terraform plan  -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
# ... when done learning, avoid ongoing cost:
terraform destroy -var-file=dev.tfvars
```

## Cost note

ECS Fargate + RDS + ALB + NAT run ~$50–100/month if left on. `dev` uses the
smallest viable sizes and a single NAT. **Run `terraform destroy` when not in use.**

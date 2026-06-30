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

## Account portability

The configuration is **account-agnostic** — no account IDs are hardcoded (the
OIDC role and bucket policies derive them at apply time). Which account you deploy
to is controlled entirely by two things:

1. **`aws_profile`** (in your tfvars) — selects the AWS account's credentials.
2. **The state backend** (`backend.hcl`) — which account's S3 bucket holds state.

To deploy the same code to a **different account**, you only change those two —
nothing in the modules or `*.tf` files.

## Bootstrapping remote state (one-time, per account)

Use the helper script — it creates the S3 state bucket + DynamoDB lock table for
whatever profile/region you pass (idempotent):

```bash
./bootstrap-state.sh --profile hrms-personal --region ap-south-1 \
  --bucket my-hrms-tfstate-<unique> --table hrms-tf-locks
```

## Usage

```bash
cd envs/dev
cp backend.hcl.example backend.hcl   # fill in the bucket/table from bootstrap
cp dev.tfvars.example  dev.tfvars     # set aws_profile + site_bucket_name

terraform init -backend-config=backend.hcl
terraform plan  -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
# ... when done learning, avoid ongoing cost:
terraform destroy -var-file=dev.tfvars
```

### Deploying to a new account later

```bash
# 1. bootstrap state in the new account
./bootstrap-state.sh --profile other-acct --region ap-south-1 --bucket other-tfstate-xyz
# 2. point at it + set the new profile, then re-init
cd envs/dev
# edit backend.hcl (new bucket) and dev.tfvars (aws_profile = "other-acct")
terraform init -reconfigure -backend-config=backend.hcl
terraform apply -var-file=dev.tfvars
```

## Cost note

ECS Fargate + RDS + ALB + NAT run ~$50–100/month if left on. `dev` uses the
smallest viable sizes and a single NAT. **Run `terraform destroy` when not in use.**

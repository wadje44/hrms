# Deployment Guide

End-to-end flow for getting Prabha HRMS running on AWS via Terraform + GitHub Actions.

## One-time setup

1. **Bootstrap remote state** (S3 bucket + DynamoDB lock table) — see `infra/README.md`.
2. **Provision infrastructure**:
   ```bash
   cd infra/envs/dev
   cp dev.tfvars.example dev.tfvars   # edit site_bucket_name + github_repo
   terraform init -backend-config=...  # see infra/README.md
   terraform apply -var-file=dev.tfvars
   ```
   > The ECS service is created before any image exists, so tasks won't start
   > until the first deploy pushes one. That's expected.
3. **Capture Terraform outputs** and set them as **GitHub repo Variables**
   (Settings → Secrets and variables → Actions → Variables):

   | Variable | Source (`terraform output`) |
   |----------|------------------------------|
   | `AWS_REGION` | your region (e.g. `ap-south-1`) |
   | `AWS_DEPLOY_ROLE_ARN` | `ci_deploy_role_arn` |
   | `ECR_REPOSITORY` | repo name part of `ecr_repository_url` |
   | `ECS_CLUSTER` | `ecs_cluster_name` |
   | `ECS_SERVICE` | `ecs_service_name` |
   | `ECS_TASK_FAMILY` | `ecs_task_family` |
   | `FRONTEND_BUCKET` | `frontend_bucket` |
   | `CLOUDFRONT_DISTRIBUTION_ID` | `cloudfront_distribution_id` |
   | `API_URL` | `api_url` |

   For the Terraform workflow also set: `AWS_TERRAFORM_ROLE_ARN`,
   `TF_STATE_BUCKET`, `TF_LOCK_TABLE`, `TF_VAR_site_bucket_name`,
   `TF_VAR_github_repo`.

## Continuous integration (`.github/workflows/ci.yml`)

Runs on every PR and push to `main`:
- **Backend** — `ruff` lint, Alembic migrate against a Postgres service, `pytest`
  (including the DB-backed API tests via `RUN_DB_TESTS=1`).
- **Frontend** — `eslint`, `tsc`, `vite build`.
- **Terraform** — `fmt -check` + `validate` for dev and prod.

## Continuous deployment (`.github/workflows/deploy.yml`)

Runs on push to `main` (auth via GitHub OIDC — no static AWS keys):
1. Build the API image, push to ECR (tagged with the commit SHA + `latest`).
2. Register a new ECS task definition revision with that image.
3. Run **migrations** as a one-off Fargate task (`alembic upgrade head`); fails the
   deploy if migrations fail.
4. Roll the ECS service to the new revision and wait for it to stabilise.
5. Build the SPA (with `VITE_API_URL`), sync to S3, invalidate CloudFront.

## Infrastructure changes (`.github/workflows/terraform.yml`)

- PRs touching `infra/**` get a `terraform plan`.
- Merges to `main` run `terraform apply`, gated by the `infra-dev` GitHub
  Environment (add required reviewers there for a manual approval gate).

## Tearing down (avoid ongoing cost)

```bash
cd infra/envs/dev
terraform destroy -var-file=dev.tfvars
```

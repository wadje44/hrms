#!/usr/bin/env bash
# Bootstrap the Terraform remote-state backend (S3 bucket + DynamoDB lock table)
# for a given AWS account. Run once per account before `terraform init`.
#
# Usage:
#   ./bootstrap-state.sh --profile hrms-personal --region ap-south-1 \
#       --bucket my-hrms-tfstate-12345 --table hrms-tf-locks
#
# Idempotent: skips resources that already exist. The account is selected purely
# by --profile, so pointing at a different account is just a different profile.
set -euo pipefail

PROFILE=""
REGION="ap-south-1"
BUCKET=""
TABLE="hrms-tf-locks"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2;;
    --region)  REGION="$2"; shift 2;;
    --bucket)  BUCKET="$2"; shift 2;;
    --table)   TABLE="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

[[ -z "$PROFILE" ]] && { echo "ERROR: --profile is required (never defaults, to avoid the wrong account)" >&2; exit 1; }
[[ -z "$BUCKET" ]] && { echo "ERROR: --bucket is required (must be globally unique)" >&2; exit 1; }

AWS="aws --profile $PROFILE --region $REGION"
ACCOUNT=$($AWS sts get-caller-identity --query Account --output text)
echo "Bootstrapping state in account $ACCOUNT ($REGION) via profile '$PROFILE'"

# --- S3 state bucket ---
if $AWS s3api head-bucket --bucket "$BUCKET" 2>/dev/null; then
  echo "Bucket $BUCKET already exists — skipping."
else
  if [[ "$REGION" == "us-east-1" ]]; then
    $AWS s3api create-bucket --bucket "$BUCKET"
  else
    $AWS s3api create-bucket --bucket "$BUCKET" \
      --create-bucket-configuration "LocationConstraint=$REGION"
  fi
  echo "Created bucket $BUCKET."
fi

$AWS s3api put-bucket-versioning --bucket "$BUCKET" \
  --versioning-configuration Status=Enabled
$AWS s3api put-bucket-encryption --bucket "$BUCKET" \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
$AWS s3api put-public-access-block --bucket "$BUCKET" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# --- DynamoDB lock table ---
if $AWS dynamodb describe-table --table-name "$TABLE" >/dev/null 2>&1; then
  echo "Lock table $TABLE already exists — skipping."
else
  $AWS dynamodb create-table --table-name "$TABLE" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST >/dev/null
  echo "Created lock table $TABLE."
fi

echo
echo "Done. Now set these in your env backend config (backend.hcl):"
echo "  bucket         = \"$BUCKET\""
echo "  dynamodb_table = \"$TABLE\""
echo "  region         = \"$REGION\""

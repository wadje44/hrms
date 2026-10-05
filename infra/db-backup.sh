#!/usr/bin/env bash
# On-demand RDS backups for the HRMS database.
#
# Manual snapshots persist independently of the DB instance — they survive a
# `terraform destroy`, unlike automated backups. ALWAYS run `create` before
# tearing the stack down if you want to keep the data.
#
# Usage:
#   ./db-backup.sh create --profile hrms-personal            # timestamped snapshot
#   ./db-backup.sh list   --profile hrms-personal
#   ./db-backup.sh create --profile hrms-personal --db hrms-dev-db --region ap-south-1
set -euo pipefail

CMD="${1:-}"; shift || true
PROFILE=""
REGION="ap-south-1"
DB="hrms-dev-db"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2;;
    --region)  REGION="$2"; shift 2;;
    --db)      DB="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

[[ -z "$PROFILE" ]] && { echo "ERROR: --profile is required (avoids hitting the wrong account)" >&2; exit 1; }
AWS="aws --profile $PROFILE --region $REGION"

case "$CMD" in
  create)
    ID="${DB}-manual-$(date +%Y-%m-%d-%H%M%S)"
    echo "Creating snapshot $ID from $DB ..."
    $AWS rds create-db-snapshot --db-instance-identifier "$DB" --db-snapshot-identifier "$ID" \
      --query 'DBSnapshot.{id:DBSnapshotIdentifier,status:Status}' --output table
    echo "Waiting for it to complete (safe to Ctrl-C; it continues in AWS)..."
    $AWS rds wait db-snapshot-available --db-snapshot-identifier "$ID"
    echo "Snapshot $ID is available."
    ;;
  list)
    $AWS rds describe-db-snapshots --db-instance-identifier "$DB" \
      --query 'reverse(sort_by(DBSnapshots,&SnapshotCreateTime))[].{id:DBSnapshotIdentifier,type:SnapshotType,status:Status,created:SnapshotCreateTime,gb:AllocatedStorage}' \
      --output table
    ;;
  *)
    echo "Usage: $0 {create|list} --profile <p> [--region <r>] [--db <id>]" >&2
    exit 1
    ;;
esac

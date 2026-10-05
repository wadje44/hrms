# Database Restore via Terraform (`snapshot_identifier`)

The RDS module supports restoring the database **through Terraform** from a
snapshot, so a disaster recovery is just a normal `terraform apply` and your
infrastructure state stays consistent — no manual `aws rds` surgery, no drift.

This is the clean, IaC-native counterpart to the CLI restore steps in
[`DISASTER-RECOVERY.md`](DISASTER-RECOVERY.md).

## How it works

`infra/modules/rds` takes a `snapshot_identifier` variable, surfaced per
environment as `db_snapshot_identifier`:

- **Empty (default)** → a fresh, empty database is created (normal case).
- **Set to a snapshot ID** → on a **fresh create**, the DB is restored from that
  snapshot with all the Terraform-managed settings (subnet group, security group,
  encryption, backups). `db_name`/`username` come from the snapshot; the master
  password is reset to the value in Secrets Manager so `DATABASE_URL` stays valid.

`snapshot_identifier` is in `ignore_changes`, so it only takes effect **at create
time**. Toggling it on an already-running DB does nothing (it will never silently
replace/destroy a live database). To restore, you apply it against a *new* DB —
i.e. after a `terraform destroy`, or into a new environment.

## Find a snapshot ID

```bash
./infra/db-backup.sh list --profile hrms-personal
# e.g. hrms-dev-manual-2026-07-02   (manual — survives destroy)
#      rds:hrms-dev-db-2026-07-01-20-46   (automated)
```

## Restore procedure (dev)

Because the restore happens at create time, you restore into a freshly-created
instance. The safe flow:

```bash
cd infra/envs/dev

# 1. If a broken instance still exists, remove just the DB from Terraform.
#    (Take a snapshot first if it holds anything you want!)
terraform destroy -target=module.rds.aws_db_instance.this -var-file=dev.tfvars

# 2. Recreate the DB from the snapshot.
terraform apply -var-file=dev.tfvars \
  -var="db_snapshot_identifier=hrms-dev-manual-2026-07-02"

# 3. The database-url secret is rebuilt from the new endpoint automatically.
#    Force the app to pick it up:
aws ecs update-service --profile hrms-personal --region ap-south-1 \
  --cluster hrms-dev-cluster --service hrms-dev-svc --force-new-deployment
```

To make the choice permanent (so future applies keep restoring from it until you
clear it), set it in your tfvars instead of `-var`:

```hcl
# dev.tfvars
db_snapshot_identifier = "hrms-dev-manual-2026-07-02"
```

> Set it back to `""` once you're on a healthy restored DB, so a later
> create doesn't unexpectedly restore an old snapshot.

## Full-rebuild disaster (whole stack was destroyed)

```bash
cd infra/envs/dev
cp backend.hcl.example backend.hcl   # if not present
terraform init -backend-config=backend.hcl
terraform apply -var-file=dev.tfvars \
  -var="db_snapshot_identifier=hrms-dev-manual-2026-07-02"
```

Everything (VPC, ECS, ALB, CloudFront) is recreated and the database comes back
from the snapshot — a complete environment restore from one command.

## Which restore method to use

| Situation | Method |
|---|---|
| Data corrupted, DB still up, need a specific timestamp | **PITR** via CLI — see [`DISASTER-RECOVERY.md`](DISASTER-RECOVERY.md) |
| DB/instance lost, or full stack rebuild | **`db_snapshot_identifier`** (this doc) — clean and IaC-consistent |
| Quick throwaway copy to inspect data | CLI `restore-db-instance-from-db-snapshot` into a temp instance |

# Disaster Recovery — Database

The HRMS data lives in one RDS PostgreSQL instance (`hrms-dev-db`). There are
three backup layers; use them together.

## Backup layers

| Layer | What | Retention | Survives `terraform destroy`? |
|---|---|---|---|
| **Automated backups** | Daily snapshot + transaction logs → point-in-time recovery (PITR) | 7 days (dev) | ❌ deleted with the instance |
| **Manual snapshots** | On-demand full snapshot (`db-backup.sh create`) | Until you delete them | ✅ **yes** |
| **Final snapshot** | Optional snapshot taken automatically on destroy | Until deleted | ✅ yes (if enabled) |

> ⚠️ In cheap mode you `terraform destroy` to save cost. Automated backups are
> **deleted** when the instance is destroyed — so **take a manual snapshot first**:
> ```
> ./infra/db-backup.sh create --profile hrms-personal
> ```

## Taking backups

```bash
# On-demand snapshot (do this before any destroy, or before risky changes)
./infra/db-backup.sh create --profile hrms-personal

# See all snapshots (manual + automated)
./infra/db-backup.sh list --profile hrms-personal
```

## Restoring

RDS restores never overwrite an existing instance — they create a **new** one.
So restore into a new identifier, verify, then repoint the app.

### A. Point-in-time recovery (data corruption / bad deploy, instance still exists)
```bash
aws rds restore-db-instance-to-point-in-time --profile hrms-personal --region ap-south-1 \
  --source-db-instance-identifier hrms-dev-db \
  --target-db-instance-identifier hrms-dev-db-restored \
  --restore-time 2026-07-02T10:00:00Z \
  --no-multi-az --db-subnet-group-name hrms-dev-db-subnets
```

### B. Restore from a snapshot (instance lost / after destroy)
```bash
aws rds restore-db-instance-from-db-snapshot --profile hrms-personal --region ap-south-1 \
  --db-instance-identifier hrms-dev-db-restored \
  --db-snapshot-identifier <snapshot-id-from-list> \
  --db-subnet-group-name hrms-dev-db-subnets
```

### Repoint the app to the restored instance
The app reads `DATABASE_URL` from Secrets Manager (`hrms-dev/database-url`), built
from the RDS endpoint. After restoring:
1. Get the new endpoint: `aws rds describe-db-instances --db-instance-identifier hrms-dev-db-restored --query 'DBInstances[0].Endpoint.Address'`
2. Update the secret value with the new host (keep the same user/password/db), **or**
   rename the restored instance to `hrms-dev-db` and re-run `terraform apply` so the
   secret is rebuilt.
3. Force a new ECS deployment so tasks pick up the change:
   `aws ecs update-service --cluster hrms-dev-cluster --service hrms-dev-svc --force-new-deployment`

## Optional: stronger DR
- **Final snapshot on destroy** — set `skip_final_snapshot = false` + a
  `final_snapshot_identifier` in the RDS module if you want destroy to auto-snapshot.
- **Cross-region copy** — `aws rds copy-db-snapshot` into a second region for
  region-failure protection.
- **Logical dumps** — a scheduled `pg_dump` to S3 gives engine-portable, restorable
  backups (useful if migrating off RDS). Can be run as a scheduled ECS task.

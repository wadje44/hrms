terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.name}-db-subnets"
  subnet_ids = var.private_subnet_ids
  tags       = var.tags
}

resource "aws_security_group" "db" {
  name        = "${var.name}-db-sg"
  description = "Postgres access from the application only"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Postgres from app"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.app_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_db_instance" "this" {
  identifier     = "${var.name}-db"
  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  # When restoring from a snapshot, db_name/username are inherited from it and
  # must not be set; the master password is reset to var.db_password so the
  # DATABASE_URL secret stays valid.
  snapshot_identifier = var.snapshot_identifier != "" ? var.snapshot_identifier : null
  db_name             = var.snapshot_identifier == "" ? var.db_name : null
  username            = var.snapshot_identifier == "" ? var.db_username : null
  password            = var.db_password
  port                = 5432

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.db.id]
  multi_az               = var.multi_az
  publicly_accessible    = false

  backup_retention_period = var.backup_retention_period
  deletion_protection     = var.deletion_protection
  skip_final_snapshot     = var.skip_final_snapshot

  tags = var.tags

  lifecycle {
    # snapshot_identifier only matters at create time. Ignoring later changes
    # means toggling it never triggers a destructive replace of a running DB —
    # a restore is done on a fresh instance (see docs/DATABASE-RESTORE.md).
    ignore_changes = [snapshot_identifier]
  }
}

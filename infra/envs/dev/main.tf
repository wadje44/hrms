data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

# ---- Network ----
module "network" {
  source         = "../../modules/network"
  name           = var.name
  azs            = local.azs
  one_nat_per_az = false
  enable_nat     = !var.cheap_mode # cheap mode skips the ~$32/mo NAT gateway
}

# ---- Container registry ----
module "ecr" {
  source = "../../modules/ecr"
  name   = "${var.name}-api"
}

# ---- Secrets (JWT + DB password) ----
module "secrets" {
  source = "../../modules/secrets"
  name   = var.name
}

# ---- App security group (shared by ECS + referenced by RDS) ----
# Created here, not in the ECS module, to avoid an ECS<->RDS cycle.
resource "aws_security_group" "app" {
  name        = "${var.name}-app-sg"
  description = "App tasks: ingress from ALB, egress anywhere"
  vpc_id      = module.network.vpc_id

  ingress {
    description     = "From ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [module.alb.security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---- Load balancer ----
module "alb" {
  source            = "../../modules/alb"
  name              = var.name
  vpc_id            = module.network.vpc_id
  public_subnet_ids = module.network.public_subnet_ids
  app_port          = 8000
  # certificate_arn left empty -> HTTP only in dev.
}

# ---- Database ----
module "rds" {
  source                = "../../modules/rds"
  name                  = var.name
  vpc_id                = module.network.vpc_id
  private_subnet_ids    = module.network.private_subnet_ids
  app_security_group_id = aws_security_group.app.id
  db_password           = module.secrets.db_password
}

# ---- DATABASE_URL secret (built from RDS endpoint + DB password) ----
resource "aws_secretsmanager_secret" "database_url" {
  name                    = "${var.name}/database-url"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id = aws_secretsmanager_secret.database_url.id
  secret_string = format(
    "postgresql+psycopg://%s:%s@%s:%s/%s",
    "hrms",
    module.secrets.db_password,
    module.rds.endpoint,
    module.rds.port,
    module.rds.db_name,
  )
}

# ---- ECS Fargate service ----
module "ecs" {
  source                    = "../../modules/ecs"
  name                      = var.name
  vpc_id                    = module.network.vpc_id
  subnet_ids                = var.cheap_mode ? module.network.public_subnet_ids : module.network.private_subnet_ids
  assign_public_ip          = var.cheap_mode
  service_security_group_id = aws_security_group.app.id
  target_group_arn          = module.alb.target_group_arn
  image                     = "${module.ecr.repository_url}:${var.image_tag}"
  app_port                  = 8000
  desired_count             = var.desired_count
  listener_dependency       = module.alb.listener_arns

  environment = [
    { name = "ENV", value = "production" },
    { name = "CORS_ORIGINS", value = "https://${module.frontend.domain_name}" },
  ]

  secrets = [
    { name = "DATABASE_URL", valueFrom = aws_secretsmanager_secret.database_url.arn },
    { name = "JWT_SECRET", valueFrom = module.secrets.jwt_secret_arn },
  ]

  secret_arns = [
    aws_secretsmanager_secret.database_url.arn,
    module.secrets.jwt_secret_arn,
  ]
}

# ---- Frontend hosting ----
module "frontend" {
  source            = "../../modules/frontend"
  bucket_name       = var.site_bucket_name
  api_origin_domain = module.alb.dns_name # serve the API at /api/* over HTTPS
}

# ---- CI deploy role (GitHub OIDC) ----
module "iam_oidc" {
  source               = "../../modules/iam_oidc"
  name                 = var.name
  github_repo          = var.github_repo
  create_oidc_provider = var.create_oidc_provider
  ecr_repository_arn   = module.ecr.repository_arn
  site_bucket_arn      = "arn:aws:s3:::${var.site_bucket_name}"
  pass_role_arns       = [module.ecs.execution_role_arn, module.ecs.task_role_arn]
}

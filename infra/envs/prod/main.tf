data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

module "network" {
  source         = "../../modules/network"
  name           = var.name
  azs            = local.azs
  one_nat_per_az = true # HA NAT in prod
}

module "ecr" {
  source = "../../modules/ecr"
  name   = "${var.name}-api"
}

module "secrets" {
  source                  = "../../modules/secrets"
  name                    = var.name
  recovery_window_in_days = 7
}

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

module "alb" {
  source            = "../../modules/alb"
  name              = var.name
  vpc_id            = module.network.vpc_id
  public_subnet_ids = module.network.public_subnet_ids
  app_port          = 8000
  certificate_arn   = var.alb_certificate_arn
}

module "rds" {
  source                = "../../modules/rds"
  name                  = var.name
  vpc_id                = module.network.vpc_id
  private_subnet_ids    = module.network.private_subnet_ids
  app_security_group_id = aws_security_group.app.id
  db_password           = module.secrets.db_password

  instance_class          = "db.t4g.small"
  multi_az                = true
  backup_retention_period = 7
  deletion_protection     = true
  skip_final_snapshot     = false
}

resource "aws_secretsmanager_secret" "database_url" {
  name                    = "${var.name}/database-url"
  recovery_window_in_days = 7
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

module "ecs" {
  source                    = "../../modules/ecs"
  name                      = var.name
  vpc_id                    = module.network.vpc_id
  subnet_ids                = module.network.private_subnet_ids
  service_security_group_id = aws_security_group.app.id
  target_group_arn          = module.alb.target_group_arn
  image                     = "${module.ecr.repository_url}:${var.image_tag}"
  app_port                  = 8000
  desired_count             = var.desired_count
  cpu                       = 512
  memory                    = 1024
  container_insights        = true
  listener_dependency       = module.alb.listener_arns

  environment = [
    { name = "ENV", value = "production" },
    {
      name  = "CORS_ORIGINS",
      value = length(var.frontend_aliases) > 0 ? "https://${var.frontend_aliases[0]}" : "https://${module.frontend.domain_name}"
    },
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

module "frontend" {
  source              = "../../modules/frontend"
  bucket_name         = var.site_bucket_name
  aliases             = var.frontend_aliases
  acm_certificate_arn = var.cloudfront_certificate_arn
  price_class         = "PriceClass_200"
}

module "iam_oidc" {
  source               = "../../modules/iam_oidc"
  name                 = var.name
  github_repo          = var.github_repo
  create_oidc_provider = var.create_oidc_provider
  ecr_repository_arn   = module.ecr.repository_arn
  site_bucket_arn      = "arn:aws:s3:::${var.site_bucket_name}"
  pass_role_arns       = [module.ecs.execution_role_arn, module.ecs.task_role_arn]
}

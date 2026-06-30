terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

data "aws_region" "current" {}

resource "aws_ecs_cluster" "this" {
  name = "${var.name}-cluster"
  setting {
    name  = "containerInsights"
    value = var.container_insights ? "enabled" : "disabled"
  }
  tags = var.tags
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.name}"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

# The service security group is created in the composition and passed in, to
# avoid an ECS<->RDS dependency cycle (RDS must allow this SG; ECS needs the
# RDS endpoint for DATABASE_URL).

# ---- IAM: task execution role (pull image, write logs, read secrets) ----
data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "execution" {
  name               = "${var.name}-exec-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "execution_managed" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Allow the execution role to read the secrets injected into the container.
data "aws_iam_policy_document" "read_secrets" {
  count = length(var.secret_arns) > 0 ? 1 : 0
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = var.secret_arns
  }
}

resource "aws_iam_role_policy" "execution_secrets" {
  count  = length(var.secret_arns) > 0 ? 1 : 0
  name   = "${var.name}-read-secrets"
  role   = aws_iam_role.execution.id
  policy = data.aws_iam_policy_document.read_secrets[0].json
}

# ---- IAM: task role (app runtime permissions) ----
resource "aws_iam_role" "task" {
  name               = "${var.name}-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
  tags               = var.tags
}

# ---- Task definition ----
resource "aws_ecs_task_definition" "app" {
  family                   = var.name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = var.image
      essential = true
      portMappings = [{
        containerPort = var.app_port
        protocol      = "tcp"
      }]
      environment = var.environment
      secrets     = var.secrets
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = data.aws_region.current.region
          "awslogs-stream-prefix" = "api"
        }
      }
    }
  ])

  tags = var.tags
}

# ---- Service ----
resource "aws_ecs_service" "app" {
  name            = "${var.name}-svc"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [var.service_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "api"
    container_port   = var.app_port
  }

  # Allow CI to update the running task definition without Terraform drift.
  lifecycle {
    ignore_changes = [task_definition]
  }

  depends_on = [var.listener_dependency]
  tags       = var.tags
}

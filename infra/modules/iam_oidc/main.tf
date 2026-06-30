terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

data "aws_caller_identity" "current" {}

# GitHub Actions OIDC provider — lets CI assume a role with no long-lived keys.
# Reuse an existing provider if one already exists in the account.
resource "aws_iam_openid_connect_provider" "github" {
  count           = var.create_oidc_provider ? 1 : 0
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
  tags            = var.tags
}

locals {
  provider_arn = var.create_oidc_provider ? aws_iam_openid_connect_provider.github[0].arn : var.existing_oidc_provider_arn
}

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [local.provider_arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = [for r in var.github_refs : "repo:${var.github_repo}:${r}"]
    }
  }
}

resource "aws_iam_role" "ci" {
  name               = "${var.name}-ci-deploy"
  assume_role_policy = data.aws_iam_policy_document.assume.json
  tags               = var.tags
}

# Deploy permissions: push to ECR, update ECS, sync the SPA bucket, invalidate CDN.
data "aws_iam_policy_document" "deploy" {
  statement {
    sid       = "EcrAuth"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }
  statement {
    sid = "EcrPush"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
    ]
    resources = [var.ecr_repository_arn]
  }
  statement {
    sid = "EcsDeploy"
    actions = [
      "ecs:DescribeServices",
      "ecs:DescribeTaskDefinition",
      "ecs:RegisterTaskDefinition",
      "ecs:UpdateService",
      "ecs:DescribeTasks",
      "ecs:ListTasks",
      "ecs:RunTask",
    ]
    resources = ["*"]
  }
  statement {
    sid       = "PassExecutionRoles"
    actions   = ["iam:PassRole"]
    resources = var.pass_role_arns
  }
  statement {
    sid       = "FrontendSync"
    actions   = ["s3:ListBucket", "s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = [var.site_bucket_arn, "${var.site_bucket_arn}/*"]
  }
  statement {
    sid       = "CdnInvalidate"
    actions   = ["cloudfront:CreateInvalidation"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "deploy" {
  name   = "${var.name}-ci-deploy"
  role   = aws_iam_role.ci.id
  policy = data.aws_iam_policy_document.deploy.json
}

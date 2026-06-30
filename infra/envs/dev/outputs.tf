output "api_url" {
  description = "Backend base URL (ALB)."
  value       = "http://${module.alb.dns_name}"
}

output "frontend_url" {
  description = "SPA URL (CloudFront)."
  value       = "https://${module.frontend.domain_name}"
}

output "ecr_repository_url" {
  value = module.ecr.repository_url
}

output "ecs_cluster_name" {
  value = module.ecs.cluster_name
}

output "ecs_service_name" {
  value = module.ecs.service_name
}

output "ecs_task_family" {
  value = module.ecs.task_family
}

output "frontend_bucket" {
  value = module.frontend.bucket_name
}

output "cloudfront_distribution_id" {
  value = module.frontend.distribution_id
}

output "ci_deploy_role_arn" {
  description = "Set this as AWS_DEPLOY_ROLE_ARN in GitHub repo variables."
  value       = module.iam_oidc.role_arn
}

output "db_endpoint" {
  value = module.rds.endpoint
}

output "jwt_secret_arn" {
  value = aws_secretsmanager_secret.jwt.arn
}

output "db_password_secret_arn" {
  value = aws_secretsmanager_secret.db.arn
}

output "db_password" {
  value     = random_password.db.result
  sensitive = true
}

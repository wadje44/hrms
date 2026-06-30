output "role_arn" {
  value = aws_iam_role.ci.arn
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

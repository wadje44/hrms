output "dns_name" {
  value = aws_lb.this.dns_name
}

output "zone_id" {
  value = aws_lb.this.zone_id
}

output "target_group_arn" {
  value = aws_lb_target_group.app.arn
}

output "security_group_id" {
  value = aws_security_group.alb.id
}

output "listener_arns" {
  value = compact([aws_lb_listener.http.arn, try(aws_lb_listener.https[0].arn, "")])
}

output "webhook_url" {
  value       = aws_lambda_function_url.webhook.function_url
  description = "Lambda Function URL for Telegram webhook"
}

# output "redis_endpoint" {
#   value       = aws_elasticache_serverless_cache.redis.endpoint[0].address
#   description = "Redis cluster endpoint"
# }

# DynamoDB outputs
output "dynamodb_users_table" {
  value       = aws_dynamodb_table.users.name
  description = "DynamoDB Users table name"
}

output "dynamodb_blocked_words_table" {
  value       = aws_dynamodb_table.blocked_words.name
  description = "DynamoDB Blocked Words table name"
}

output "scheduler_lambda_arn" {
  value       = aws_lambda_function.scheduler.arn
  description = "ARN of the scheduler Lambda function"
}

output "scheduler_cron_expression" {
  value       = aws_cloudwatch_event_rule.scheduler_trigger.schedule_expression
  description = "Cron expression for the scheduler trigger"
}

output "set_webhook_command" {
  sensitive = true
  value = <<-EOT
    curl -X POST "https://api.telegram.org/bot${var.bot_token}/setWebhook" -H "Content-Type: application/json" -d '{"url": "${aws_lambda_function_url.webhook.function_url}", "drop_pending_updates": true}'
  EOT
}
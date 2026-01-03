output "webhook_url" {
  value       = aws_lambda_function_url.webhook.function_url
  description = "Lambda Function URL for Telegram webhook"
}

output "redis_endpoint" {
  value       = aws_elasticache_serverless_cache.redis.endpoint[0].address
  description = "Redis cluster endpoint"
}

output "scheduler_lambda_arn" {
  value       = aws_lambda_function.scheduler.arn
  description = "ARN of the scheduler Lambda function"
}

output "scheduler_cron_expression" {
  value       = aws_cloudwatch_event_rule.scheduler_trigger.schedule_expression
  description = "Cron expression for the scheduler trigger"
}

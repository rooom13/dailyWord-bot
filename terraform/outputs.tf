output "webhook_url" {
  value       = aws_lambda_function_url.webhook.function_url
  description = "Lambda Function URL for Telegram webhook"
}

output "redis_endpoint" {
  value       = aws_elasticache_serverless_cache.redis.endpoint[0].address
  description = "Redis cluster endpoint"
}

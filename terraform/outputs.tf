output "webhook_url" {
  value       = aws_lambda_function_url.webhook.function_url
  description = "Lambda Function URL for Telegram webhook"
}

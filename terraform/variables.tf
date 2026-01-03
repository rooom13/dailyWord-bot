variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "daily-word-bot"
}

variable "bot_token" {
  description = "Telegram Bot Token"
  type        = string
  sensitive   = true
}

variable "admin_chat_ids" {
  description = "Comma separated admin chat IDs"
  type        = string
  sensitive   = true
}

variable "lambda_function_timeout_seconds" {
  description = "Timeout for the Lambda function in seconds"
  type        = number
  default     = 60
}

variable "scheduler_cron_expression" {
  description = "Cron expression for the scheduler trigger (UTC timezone)"
  type        = string
  default     = "cron(30 12 * * ? *)" # Daily at 12:30 PM UTC
}


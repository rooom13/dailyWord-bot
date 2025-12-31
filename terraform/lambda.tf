# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# S3 Bucket for Lambda code
resource "aws_s3_bucket" "lambda_code" {
  bucket_prefix = "${var.project_name}-lambda-"
  force_destroy = true
}

resource "aws_s3_object" "lambda_code" {
  bucket = aws_s3_bucket.lambda_code.id
  key    = "deployment-package.zip"
  source = "../deployment-package.zip"
  etag   = filemd5("../deployment-package.zip")
}

# Lambda Function
resource "aws_lambda_function" "webhook" {
  function_name    = "${var.project_name}-webhook"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_webhook.lambda_handler"
  s3_bucket        = aws_s3_bucket.lambda_code.id
  s3_key           = aws_s3_object.lambda_code.key
  source_code_hash = filebase64sha256("../deployment-package.zip")
  runtime          = "python3.10"
  timeout          = 60
  memory_size      = 256

  environment {
    variables = {
      BOT_TOKEN      = var.bot_token
      ADMIN_CHAT_IDS = var.admin_chat_ids
      ENV            = "live"
    }
  }
}

# Lambda Function URL
resource "aws_lambda_function_url" "webhook" {
  function_name      = aws_lambda_function.webhook.function_name
  authorization_type = "NONE"
}

resource "aws_lambda_permission" "function_url_invoke" {
  statement_id           = "FunctionURLAllowPublicAccess"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.webhook.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

resource "aws_lambda_permission" "function_url_invoke_function" {
  statement_id  = "FunctionURLInvokeAllowPublicAccess"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.webhook.function_name
  principal     = "*"
}

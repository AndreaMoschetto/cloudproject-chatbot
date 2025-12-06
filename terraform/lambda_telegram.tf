# --- 1. Package the Python code ---
data "archive_file" "telegram_zip" {
  type        = "zip"
  source_file = "../lambda/telegram_bot.py"
  output_path = "telegram_lambda.zip"
}

# --- 2. Create the Lambda ---
resource "aws_lambda_function" "telegram_bot" {
  filename         = "telegram_lambda.zip"
  function_name    = "cloud-nlp-telegram-bot"
  role             = data.aws_iam_role.lab_role.arn
  handler          = "telegram_bot.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.telegram_zip.output_base64sha256
  timeout          = 300 # A bit of time to download large PDFs
  environment {
    variables = {
      TELEGRAM_TOKEN = var.telegram_token,
      S3_BUCKET_NAME = aws_s3_bucket.pdf_bucket.id,
      ORCHESTRATOR_URL = "https://${data.aws_route53_zone.main.name}"
    }
  }
}

# --- 3. Create the Public URL (Webhook) ---
resource "aws_lambda_function_url" "telegram_webhook" {
  function_name      = aws_lambda_function.telegram_bot.function_name
  authorization_type = "NONE" # Public, so Telegram can call it
}

# --- 4. Set Telegram Webhook ---
resource "null_resource" "set_telegram_webhook" {
  triggers = {
    webhook_url = aws_lambda_function_url.telegram_webhook.function_url
  }

  provisioner "local-exec" {
    command = "curl -X POST https://api.telegram.org/bot${var.telegram_token}/setWebhook?url=${aws_lambda_function_url.telegram_webhook.function_url}"
  }
}
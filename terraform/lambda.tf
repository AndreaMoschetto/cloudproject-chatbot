# --- 1. Zip the Python code for the Lambda ---
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "../lambda/trigger_ingestion.py" # Local file path
  output_path = "lambda_function.zip"
}

# --- 2. Define the Lambda Function ---
resource "aws_lambda_function" "ingestion_trigger" {
  filename         = "lambda_function.zip"
  function_name    = "cloud-nlp-ingestion-trigger"
  role             = data.aws_iam_role.lab_role.arn
  handler          = "trigger_ingestion.lambda_handler" # FileName.FunctionName
  runtime          = "python3.11"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 30 # seconds

  environment {
    variables = {
      RAG_INGEST_API_URL = "https://${data.aws_route53_zone.main.name}/ingest-s3"
    }
  }
}

# --- 3. Permission: S3 can invoke this Lambda ---
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingestion_trigger.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.pdf_bucket.arn
}

# --- 4. The Trigger: When S3 receives a file, it calls Lambda ---
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.pdf_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.ingestion_trigger.arn
    events              = ["s3:ObjectCreated:*"] # Triggers on Upload, Copy, etc.
    filter_suffix       = ".pdf" # Triggers only for PDFs
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
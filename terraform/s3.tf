resource "aws_s3_bucket" "pdf_bucket" {
  bucket_prefix = "cloud-nlp-docs-" # Generates a unique name like cloud-nlp-docs-xyz123
  force_destroy = true # Allows deletion even if the bucket is not empty
}

# Blocks public access (Best Practice of security)
resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = aws_s3_bucket.pdf_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
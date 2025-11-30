output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.users.id
}

output "cognito_client_id" {
  value = aws_cognito_user_pool_client.client.id
}

output "cognito_client_secret" {
  value = aws_cognito_user_pool_client.client.client_secret
  sensitive = true
}

output "cognito_domain" {
  value = "https://${aws_cognito_user_pool_domain.main.domain}.auth.us-east-1.amazoncognito.com"
}

output "s3_bucket_name" {
  value = aws_s3_bucket.pdf_bucket.id
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.chat_history.name
}

output "ecr_repos" {
  value = [
    aws_ecr_repository.frontend.repository_url,
    aws_ecr_repository.orchestrator.repository_url,
    aws_ecr_repository.rag_service.repository_url
  ]
}
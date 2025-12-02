resource "aws_cloudwatch_log_group" "frontend_logs" {
  name              = "/ecs/cloud-nlp-frontend"
  retention_in_days = 1
}

resource "aws_cloudwatch_log_group" "backend_logs" {
  name              = "/ecs/cloud-nlp-backend"
  retention_in_days = 1
}
resource "aws_ecr_repository" "frontend" {
  name = "cloud-nlp/frontend"
  force_delete = true
}

resource "aws_ecr_repository" "orchestrator" {
  name = "cloud-nlp/orchestrator"
  force_delete = true
}

resource "aws_ecr_repository" "rag_service" {
  name = "cloud-nlp/rag-service"
  force_delete = true
}
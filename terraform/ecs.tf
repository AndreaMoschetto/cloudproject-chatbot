# --- Cluster ECS ---
resource "aws_ecs_cluster" "main" {
  name = "cloud-nlp-cluster"
}

# Import existing IAM Role
data "aws_iam_role" "lab_role" {
  name = "LabRole"
}

# --- IAM Roles ---
# Execution Role: Makes ECS able to pull images and publish logs
# resource "aws_iam_role" "execution_role" {
#   name = "cloud-nlp-execution-role"
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" } }]
#   })
# }
# resource "aws_iam_role_policy_attachment" "execution_role_policy" {
#   role       = aws_iam_role.execution_role.name
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
# }

# # Task Role: Allows python code to use DynamoDB, S3, etc.
# resource "aws_iam_role" "task_role" {
#   name = "cloud-nlp-task-role"
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" } }]
#   })
# }

# resource "aws_iam_role_policy" "task_access" {
#   name = "task-access"
#   role = aws_iam_role.task_role.id
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       { Action = ["dynamodb:*", "s3:*", "sqs:*", "cognito-idp:*"], Effect = "Allow", Resource = "*" }
#     ]
#   })
# }

# --- TASK DEFINITION: FRONTEND ---
resource "aws_ecs_task_definition" "frontend" {
  family                   = "cloud-nlp-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256" # 0.25 vCPU
  memory                   = "512" # 0.5 GB RAM
  execution_role_arn = data.aws_iam_role.lab_role.arn
  task_role_arn      = data.aws_iam_role.lab_role.arn

  container_definitions = jsonencode([{
    name  = "frontend"
    image = aws_ecr_repository.frontend.repository_url
    portMappings = [{ containerPort = 8000 }]
    
    environment = [
      { name = "BACKEND_URL", value = "http://${aws_lb.main.dns_name}" }, # Points to the public Load Balancer
      { name = "CHAINLIT_AUTH_SECRET", value = "SuperSegretoCloud123" },
      { name = "CHAINLIT_URL", value = "https://am-cloudnlpchatbot.site" }, # Makes chainlit aware of the public URL, avoiding redirect issues
      # Dynamic Cognito Configuration
      { name = "OAUTH_COGNITO_CLIENT_ID", value = aws_cognito_user_pool_client.client.id },
      { name = "OAUTH_COGNITO_CLIENT_SECRET", value = aws_cognito_user_pool_client.client.client_secret },
      { name = "OAUTH_COGNITO_DOMAIN", value = "${aws_cognito_user_pool_domain.main.domain}.auth.us-east-1.amazoncognito.com" },
      { name = "OAUTH_COGNITO_SCOPE", value = "openid profile email" }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/cloud-nlp-frontend"
        "awslogs-region"        = "us-east-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# --- TASK DEFINITION: BACKEND (Orchestrator + RAG) ---
resource "aws_ecs_task_definition" "backend" {
  family                   = "cloud-nlp-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048" # 2 vCPU (più veloce)
  memory                   = "4096" # 4 GB RAM (respiro per l'AI)
  execution_role_arn = data.aws_iam_role.lab_role.arn
  task_role_arn      = data.aws_iam_role.lab_role.arn

  container_definitions = jsonencode([
    # Container A: Orchestrator (Lightweight)
    {
      name  = "orchestrator"
      image = aws_ecr_repository.orchestrator.repository_url
      portMappings = [{ containerPort = 8001 }]
      environment = [
        { name = "RAG_SERVICE_URL", value = "http://127.0.0.1:8002" }, # Localhost since both containers are in the same task
        { name = "USE_DYNAMODB", value = "true" },
        { name = "DYNAMODB_TABLE", value = aws_dynamodb_table.chat_history.name }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = { "awslogs-group" = "/ecs/cloud-nlp-backend", "awslogs-region" = "us-east-1", "awslogs-stream-prefix" = "orchestrator" }
      }
    },
    # Container B: RAG Service (Heavy)
    {
      name  = "rag-service"
      image = aws_ecr_repository.rag_service.repository_url
      portMappings = [{ containerPort = 8002 }]
      environment = [
        { name = "PYTHONUNBUFFERED", value = "1" }, # Ensures real-time logging
        { name = "S3_BUCKET_NAME", value = aws_s3_bucket.pdf_bucket.id },
        { name = "GOOGLE_API_KEY", value = var.google_api_key },
        { name = "CHROMA_DIR", value = "/app/chroma_db" },
        { name = "DATA_DIR", value = "/app/data" },
        { name = "NUM_DOCS", value = "5" },
        { name = "CHROMA_SERVER_HOST", value = "127.0.0.1" },
        { name = "CHROMA_SERVER_PORT", value = "8000" },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = { "awslogs-group" = "/ecs/cloud-nlp-backend", "awslogs-region" = "us-east-1", "awslogs-stream-prefix" = "rag" }
      }
    },
    # ChromaDB Server (Pulito, porta standard 8000)
    {
      name  = "chroma-server"
      image = "chromadb/chroma:latest"
      portMappings = [{ containerPort = 8000 }]
      environment = [
        { name = "IS_PERSISTENT", value = "TRUE" }
      ]
      logConfiguration = {
        logDriver = "awslogs", options = { "awslogs-group" = "/ecs/cloud-nlp-backend", "awslogs-region" = "us-east-1", "awslogs-stream-prefix" = "chroma" }
      }
    }
  ])
}

# --- SERVICES ---

resource "aws_ecs_service" "frontend" {
  name            = "cloud-nlp-frontend-svc"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true # Usefull for saving costs on NAT Gateway
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = 8000
  }
}

resource "aws_ecs_service" "backend" {
  name            = "cloud-nlp-backend-svc"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "orchestrator"
    container_port   = 8001
  }
}
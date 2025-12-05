# --- Application Load Balancer ---
resource "aws_lb" "main" {
  name               = "cloud-nlp-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb_sg.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

# --- Listener () ---
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

# --- Routing Rules ---
# If the URL starts with /query or /history or /docs, send to Backend
resource "aws_lb_listener_rule" "backend_rule" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/query", "/history/*", "/docs", "/openapi.json", "/ingest-s3"]
    }
  }
}

# --- Target Groups ---

# 1. Frontend
resource "aws_lb_target_group" "frontend" {
  name        = "cloud-nlp-frontend-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip" # Necessary for Fargate
  
  health_check {
    path    = "/login" # Chainlit responds here
    matcher = "200-302"
  }
}

# 2. Backend
resource "aws_lb_target_group" "backend" {
  name        = "cloud-nlp-backend-tg"
  port        = 8001
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path = "/docs" # FastAPI responds here by default
  }
}
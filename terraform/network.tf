# --- VPC ---
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "cloud-nlp-vpc" }
}

# --- Internet Gateway ---
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags = { Name = "cloud-nlp-igw" }
}

# --- Subnets ---
resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true # Foundamental for saving money on NAT Gateways
  tags = { Name = "cloud-nlp-public-1" }
}                                               


resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id  
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"        
  map_public_ip_on_launch = true # Same as above
  tags = { Name = "cloud-nlp-public-2" }
}

# --- Routing ---
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# --- Security Groups ---
# SG for the Load Balancer (Open to the world on port 80)
resource "aws_security_group" "lb_sg" {
  name        = "cloud-nlp-lb-sg"
  description = "Allow HTTP and HTTPS traffic to Load Balancer"
  vpc_id      = aws_vpc.main.id

  # Rule for HTTP (80)
  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  # --- RULE FOR HTTPS (443) ---
  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }
  # ------------------------------------

  # Egress allowed everywhere
  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# SG for the ECS Containers (Only allow traffic from the LB SG)
resource "aws_security_group" "ecs_sg" {
  name        = "cloud-nlp-ecs-sg"
  description = "Allow traffic only from ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    protocol        = "tcp"
    from_port       = 0
    to_port         = 65535
    security_groups = [aws_security_group.lb_sg.id] 
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}
# 5. Infrastructure as Code (IaC) with Terraform

The entire AWS infrastructure described in this project was not created manually via console, but is defined via code using **Terraform**. This approach ensures reproducibility, infrastructure versioning, and drastically reduces human error.

## Module Organization
The Terraform code was structured into modular files to improve readability and maintenance:

| File (`terraform/`) | Description |
| :--- | :--- |
| `main.tf` | AWS provider configuration and Terraform version. |
| `network.tf` | Definition of VPC, Public Subnets, Internet Gateway, and Route Tables. |
| `alb.tf` | Application Load Balancer, Target Groups, and Listener Rules (HTTP). |
| `dns.tf` | Management of Route53 zone, ACM certificate, and HTTPS Listener. |
| `ecs.tf` | ECS Cluster, Task Definitions (Frontend and Backend), and Fargate Services. |
| `ecr.tf` | Repository for Docker images (Frontend, Orchestrator, RAG). |
| `s3.tf` | S3 Bucket for documents, with public access block policy. |
| `dynamodb.tf` | NoSQL table for chat history. |
| `cognito.tf` | User Pool, App Client, and Domain for authentication. |
| `lambda.tf` | Lambda for S3 trigger and related permissions. |
| `lambda_telegram.tf` | Lambda for Telegram bot, Function URL, and Webhook automation. |
| `variables.tf` & `outputs.tf`| Input variable definitions (e.g., secrets) and useful post-deploy outputs. |

## Advanced Automation
Terraform is not limited to creating static resources but also handles complex dynamic configurations:

1.  **Automatic DNS Validation:** ACM certificate creation automatically waits for validation DNS records to propagate on Route53.
2.  **Variable Injection:** Service URLs (like the ALB endpoint or Cognito domain) are dynamically injected as environment variables into ECS container definitions and Lambda Functions.
3.  **Local Provisioning (`null_resource`):** We use the `local-exec` provider to run commands on the host machine at the end of deployment, such as automating the `curl` call to register the Telegram bot Webhook.

---
<div align="center">

[← Previous Chapter](04_data_ingestion_events.md) | [🏠 Back to Home](../README.md) | [Next Chapter: Security →](06_security_and_auth.md)

</div>
# 7. CI/CD and DevOps

To ensure an agile development cycle and reliable deployments, a **Continuous Integration and Continuous Deployment (CI/CD)** pipeline was implemented using **GitHub Actions**.

## Containerization (Docker)
Each microservice (Frontend, Orchestrator, RAG Service) is defined by its own `Dockerfile`.
* They are based on `python:3.11-slim` images to reduce size and attack surface.
* They use a multi-stage build approach (where possible) or `pip` cache cleaning to optimize layers.
* The ChromaDB service uses the official `chromadb/chroma:latest` image directly from Docker Hub.

## The GitHub Actions Pipeline
The workflow (`.github/workflows/deploy.yml`) is automatically triggered on every `push` to the `main` branch. The pipeline executes the following sequential steps:

### 1. Setup & Authentication
* Source code checkout.
* AWS credentials configuration (using GitHub Repository Secrets for `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`).
* Login to the private **Amazon ECR** registry.

### 2. Build & Push (CI)
For each custom service (Frontend, Orchestrator, RAG):
* The local Docker image is built tagged as `:latest`.
* The image is uploaded (pushed) to the respective ECR repository created by Terraform.

### 3. Deployment (CD)
Once images in the registry are updated, the pipeline forces a service update on ECS Fargate:
* Command: `aws ecs update-service --force-new-deployment`.
* **Rolling Update:** ECS starts new tasks with updated images. Only when new tasks pass Load Balancer Health Checks are the old tasks terminated. This ensures deployment with zero (or minimal) downtime.

## Secret Management
Sensitive secrets (AWS credentials, Google and Telegram API Keys) are never written in the code.
1.  They reside in the developer's local `terraform.tfvars` file and inside the repository secrets github section(excluded from code).
2.  Terraform injects them as encrypted environment variables into ECS Task Definitions.
3.  Containers read them at startup via `os.getenv()`.

---
<div align="center">

[← Previous Chapter](06_security_and_auth.md) | [🏠 Back to Home](../README.md) | [Next Chapter: Telegram Integration →](08_telegram_integration.md)

</div>
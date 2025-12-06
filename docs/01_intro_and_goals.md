# 1. Introduction and Project Goals

The **CloudNLP** project was created with the goal of building an intelligent virtual assistant based on **RAG (Retrieval-Augmented Generation)** architectures, capable of answering questions about technical documents (PDFs) provided by the user in real-time.

The main challenge lies not in the AI logic, but in the design of a **Cloud-Native**, scalable, secure, and resilient infrastructure, respecting the budget constraints typical of an academic environment (AWS Learner Lab).

## Key Objectives
1.  **Microservices:** Decomposition of the application into independent components (Frontend, Orchestrator, RAG, DB).
2.  **Serverless & Managed Services:** Extensive use of managed services (Fargate, S3, DynamoDB, Cognito) to reduce operational overhead.
3.  **Event-Driven Ingestion:** Decoupling between data upload (synchronous) and processing (asynchronous) via S3 triggers and Lambda.
4.  **Security "By Design":** Implementation of HTTPS (SSL/TLS), VPC isolation, Security Group chaining, and OAuth2 authentication.
5.  **Automation:** Infrastructure as Code (Terraform) and CI/CD pipeline (GitHub Actions) to eliminate manual interventions.

## Technology Stack
* **Compute:** AWS ECS Fargate, AWS Lambda.
* **Storage:** Amazon S3 (Documents), Amazon DynamoDB (Chat History).
* **Vector Database:** ChromaDB (Client/Server mode).
* **Networking:** Application Load Balancer (ALB), Route53, ACM.
* **Auth:** Amazon Cognito.
* **AI/LLM:** LangChain, Google Gemini Pro, HuggingFace Embeddings.
* **DevOps:** Terraform, Docker, GitHub Actions.
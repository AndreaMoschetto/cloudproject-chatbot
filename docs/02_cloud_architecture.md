# 2. Cloud Architecture and Microservices

The system architecture is designed to maximize modularity and security while minimizing management costs.

## Sidecar Pattern on ECS Fargate
The application core resides on **Amazon ECS** with **Fargate** launch type (Serverless Compute). We adopted a hybrid strategy for Task definition:

### 1. Frontend Task (Standalone)
The frontend (built with **Chainlit**) runs in a dedicated task. This allows the user interface to scale independently from the backend. It communicates with the backend exclusively via the Load Balancer's public URL, simulating a real external client.

### 2. Backend Task (Sidecar Pattern)
The backend implements the **Sidecar** pattern, grouping three containers in the same Task Definition:
* **Orchestrator (FastAPI):** The internal API Gateway. Handles authentication, chat history on DynamoDB, and routes requests.
* **RAG Service (FastAPI):** The computation engine. Handles embedding logic and LLM.
* **ChromaDB Server:** The persistent vector database.

**Sidecar Advantages:**
* **Localhost Communication:** The three containers communicate via `localhost` (loopback interface), ensuring zero latency and high security (traffic never leaves the task).
* **Resource Management:** They share the same CPU/RAM allocation (4GB), optimizing costs compared to three separate tasks.

## Networking and Load Balancing
An **Application Load Balancer (ALB)** manages all incoming traffic.
* **Routing:** Path-based rules route `/query`, `/files`, `/ingest-s3` to the Backend and the rest to the Frontend.
* **HTTPS Offloading:** The ALB terminates the secure connection (SSL) using a certificate managed by ACM, relieving containers from cryptographic load.
* **Security Groups:** The "least privilege" rule was applied. The container Security Groups accept traffic **only** originating from the Load Balancer's Security Group. No direct internet access is allowed to the containers.
# ☁️ Cloud Systems NLP Project

Welcome to the Cloud Systems course chatbot!

## 🚀 What can it do?

This assistant uses **RAG (Retrieval Augmented Generation)** to answer questions based on PDF documents uploaded by the administrator.

### 🏗️ Architecture

The system is built on a modern **Cloud Native** architecture:

  - **Frontend:** Chainlit (ECS Fargate)
  - **Backend:** FastAPI Orchestrator + RAG Service (ECS Fargate)
  - **Database:** Amazon DynamoDB (Chat History)
  - **Vector Store:** ChromaDB
  - **Auth:** Amazon Cognito
  - **Ingestion:** S3 + Lambda Triggers

### 👨‍💻 Author

Developed by **Andrea Moschetto** for the Cloud Systems course.
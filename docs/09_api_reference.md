# 9. API & Endpoint Reference

This section provides a comprehensive reference of all external entry points exposed by the CloudNLP architecture.

**Base URL:** `https://am-cloudnlpchatbot.site`

## 🖥️ User Interface

These endpoints are primarily used by web browsers and the authentication flow.

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | **Home Page**. Loads the Chainlit chat interface. | Public (Redirects to Login) |
| `GET` | `/login` | Triggers the OAuth2 flow via AWS Cognito. | Public |
| `GET` | `/logout` | Clears the session and redirects to Cognito logout. | Authenticated |
| `GET` | `/auth/oauth/cognito/callback` | Callback URL handled by Chainlit to retrieve tokens. | Internal (Browser Redirect) |

---

## ⚙️ REST API (Orchestrator)

The core logic is exposed via a REST API routed through the Application Load Balancer. These endpoints can be used by the Frontend, the Telegram Lambda, or external tools (like Postman/Curl) for debugging.

**Note:** The Load Balancer routes requests starting with these paths to the **Backend Task** (Port 8001).

| Method | Endpoint | Description | Payload / Params |
| :--- | :--- | :--- | :--- |
| `POST` | **/query** | Sends a user message to the RAG system and gets a response. | `{"query": "...", "session_id": "..."}` |
| `GET` | **/history/{session_id}** | Retrieves the full chat history for a specific user session from DynamoDB. | Path Param: `session_id` (Email) |
| `DELETE` | **/history/{session_id}** | **Clear History**. Deletes all conversation logs for the user from DynamoDB. | Path Param: `session_id` (Email) |
| `GET` | **/files** | **List Files**. Returns a JSON list of all PDF documents currently indexed in the Knowledge Base. | None |
| `DELETE` | **/files/{filename}** | **Delete File**. Removes a document from the disk storage and wipes its vectors from ChromaDB. | Path Param: `filename` |
| `POST` | **/ingest-s3** | **Trigger Ingestion**. Triggers the async ingestion pipeline. Used by Lambda. | `{"file_key": "...", "chat_id": "..."}` |
| `GET` | **/docs** | **Swagger UI**. Auto-generated interactive API documentation (FastAPI). | Public |
| `GET` | **/openapi.json** | **OpenAPI Spec**. Raw JSON definition of the API schema. | Public |

---

## 🤖 Integrations & Webhooks

These endpoints connect external platforms to the internal logic.

| Component | Type | URL / Identifier | Description |
| :--- | :--- | :--- | :--- |
| **Telegram Bot** | User Interface | `@YourBotName_bot` | The user-facing bot on the Telegram App. |
| **Telegram Webhook** | Serverless Endpoint | `https://[id].lambda-url.us-east-1.on.aws/` | Public Lambda URL invoked by Telegram servers on new messages. |
| **S3 Event** | Internal Trigger | `s3:ObjectCreated:*` | Internal AWS event that fires the `trigger_ingestion` Lambda upon file upload. |

## 📂 Repo files
```bash
cloud-nlp-project/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD Pipeline for build and deploy on AWS
├── docs/                       # Project technical documentation
│   ├── 01_intro.md
│   ├── 02_architecture.md
│   └── ...
├── frontend/                   # UI Microservice (Chainlit)
│   ├── .chainlit/              # Chainlit configuration (Auth, UI settings)
│   ├── Dockerfile              # Frontend container definition
│   ├── app.py                  # UI, Chat, and Login logic
│   └── requirements.txt        # Lightweight Python dependencies
├── lambda/                     # Serverless Functions
│   ├── telegram_bot.py         # Telegram Bot Logic (Webhook)
│   └── trigger_ingestion.py    # Trigger S3 -> Orchestrator
├── orchestrator/               # API Gateway Microservice
│   ├── Dockerfile              # Orchestrator container definition
│   ├── main.py                 # API Endpoint (Traffic router)
│   ├── database.py             # Persistence logic (DynamoDB)
│   └── requirements.txt        # Dependencies (FastAPI, Boto3)
├── rag_service/                # Core Microservice (AI & Logic)
│   ├── data/                   # Temporary folder for PDF download
│   ├── Dockerfile              # RAG container definition (with PyTorch)
│   ├── main.py                 # Internal APIs (Ingest, Generate)
│   ├── ingest.py               # PDF processing and vectorization script
│   ├── retriever.py            # ChromaDB search logic
│   ├── generator.py            # Response logic (Gemini LLM)
│   ├── constants.py            # Environment variable configuration
│   └── requirements.txt        # Heavy dependencies (LangChain, Torch)
├── terraform/                  # Infrastructure as Code (IaC)
│   ├── main.tf                 # AWS Provider Setup
│   ├── network.tf              # VPC, Subnet, Security Groups
│   ├── ecs.tf                  # Fargate Cluster and Task Definitions
│   ├── alb.tf                  # Load Balancer and Target Groups
│   ├── dns.tf                  # Route53 and ACM Certificate
│   ├── cognito.tf              # User Auth Configuration
│   ├── s3.tf                   # Document Storage Bucket
│   ├── lambda*.tf              # Lambda Function Definitions
│   ├── variables.tf            # Input variable definitions
│   └── outputs.tf              # Useful outputs (site URL, etc.)
├── .env                        # Environment Variables (Local)
├── .gitignore                  # Files excluded from Git (tfvars, venv, etc.)
├── docker-compose.yml          # Orchestration for local testing
├── chainlit.md                 # Welcome message in chat
└── README.md                   # Main documentation
```

---
<div align="center">

[← Previous Chapter](08_telegram_integration.md) | [🏠 Back to Home](../README.md)

</div>
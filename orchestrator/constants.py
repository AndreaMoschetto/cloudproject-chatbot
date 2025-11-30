import os

RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://rag-service:8002")

# for when using DynamoDB
USE_DYNAMODB = os.getenv("USE_DYNAMODB", "false")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "ChatHistory")

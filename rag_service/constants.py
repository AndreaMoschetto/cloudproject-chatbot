import os

DATA_DIR = os.getenv("DATA_DIR", "/app/data")
CHROMA_DIR = os.getenv("CHROMA_DIR", "/app/chroma_db")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "my_course_notes"
NUM_DOCS = int(os.getenv("NUM_DOCS", "5"))
# pdf s3 bucket
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

CHROMA_SERVER_HOST = os.getenv("CHROMA_SERVER_HOST")
CHROMA_SERVER_PORT = os.getenv("CHROMA_SERVER_PORT")

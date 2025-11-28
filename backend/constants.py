import os

DATA_DIR = os.getenv("DATA_DIR", "data/")
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_db/")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "my_course_notes"
NUM_DOCS = int(os.getenv("NUM_DOCS", "5"))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from retriever import Retriever
from generator import Generator
from constants import (
    NUM_DOCS, DATA_DIR, S3_BUCKET_NAME, CHROMA_SERVER_HOST,
    CHROMA_SERVER_PORT, COLLECTION_NAME, CHROMA_DIR, TELEGRAM_TOKEN
)
import subprocess
import boto3
import os
import sys
import requests
import chromadb

app = FastAPI()

print("Initializing RAG Service...")
retriever = Retriever(num_docs=NUM_DOCS)
generator = Generator()


class RAGRequest(BaseModel):
    query: str


class RAGResponse(BaseModel):
    answer: str
    context_used: str  # Optional: debug mode


class IngestRequest(BaseModel):
    file_key: str  # Il nome del file su S3 (es. "documenti/paper.pdf")
    chat_id: str | None = None


@app.post("/generate", response_model=RAGResponse)
def generate_response(request: RAGRequest):
    try:
        print(f"Retrieving for query: {request.query}")
        context = retriever.get_context(request.query)

        print("Generating answer...")
        answer = generator.generate_answer(request.query, context)

        return RAGResponse(answer=answer, context_used=context)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest-s3")
def ingest_from_s3(request: IngestRequest, background_tasks: BackgroundTasks):
    # It will be visible thanks to PYTHONUNBUFFERED
    print(f"📥 [API] Received request for: {request.file_key}")
    background_tasks.add_task(run_ingestion_background, request.file_key, request.chat_id)
    return {"status": "accepted", "message": "Ingestion started in background"}


@app.get("/files")
def list_files():
    """List all PDF files available in the DATA_DIR."""
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".pdf")]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/files/{filename}")
def delete_file(filename: str):
    """Delete a file from disk and (optionally) from the Vector Store"""
    print(f"🗑️ Request to delete: {filename}")
    file_path = os.path.join(DATA_DIR, filename)
    status_msg = []
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            status_msg.append("Deleted from Disk")
        except Exception as e:
            print(f"Error deleting file: {e}")
            raise HTTPException(status_code=500, detail=f"Disk delete failed: {e}")
    else:
        status_msg.append("File not found on Disk")

    try:
        if CHROMA_SERVER_HOST and CHROMA_SERVER_PORT:
            client = chromadb.HttpClient(host=CHROMA_SERVER_HOST, port=CHROMA_SERVER_PORT)
        else:
            client = chromadb.PersistentClient(path=CHROMA_DIR)  # Fallback
        collection = client.get_collection(name=COLLECTION_NAME)

        print(f"Removing vectors for source: {filename}...")
        collection.delete(where={"source": filename})
        status_msg.append("Deleted from Vector DB")
    except Exception as e:
        print(f"⚠️ Error deleting from Chroma: {e}")
        # We do not raise a blocking error here, maybe the file was on disk but not in the db
        status_msg.append(f"Vector DB delete failed: {str(e)}")

    return {"status": "success", "details": ", ".join(status_msg), "file": filename}


def run_ingestion_background(file_key: str, chat_id: str = None):
    print(f"🔄 [BACKGROUND] Starting ingestion logic for: {file_key}")
    try:
        s3 = boto3.client('s3')
        filename = os.path.basename(file_key)
        local_path = os.path.join(DATA_DIR, filename)

        print(f"⬇️ Downloading {file_key} from S3...")
        s3.download_file(S3_BUCKET_NAME, file_key, local_path)

        print(f"🗑️ Deleting {file_key} from S3...")
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=file_key)

        print(f"🚀 Launching ingest.py subprocess for {file_key}...")
        process = subprocess.Popen(
            ["python", "ingest.py", "--file", filename],
            stdout=sys.stdout,  # direct logs on CloudWatch
            stderr=sys.stderr,
            text=True
        )
        process.wait()  # no problem here, it's background task
        if process.returncode == 0:
            msg = f"✅ Ingestion completed for **{filename}**!"
            if chat_id:
                send_telegram_notification(chat_id, msg)
        else:
            msg = f"❌ Ingestion error for **{filename}**."
            if chat_id:
                send_telegram_notification(chat_id, msg)

    except Exception as e:
        print(f"💀 Critical Background Error: {e}")
        if chat_id:
            send_telegram_notification(chat_id, f"🔥 Critical system error: {str(e)}")


def send_telegram_notification(chat_id, message):
    """Invia un messaggio di notifica all'utente Telegram"""
    if not chat_id or not TELEGRAM_TOKEN:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"⚠️ Failed to send Telegram notification: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Note: Port 8002 internal

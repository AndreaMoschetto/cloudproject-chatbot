from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from retriever import Retriever
from generator import Generator
from constants import NUM_DOCS, DATA_DIR, S3_BUCKET_NAME
import subprocess
import boto3
import os
import sys

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
    background_tasks.add_task(run_ingestion_background, request.file_key)
    return {"status": "accepted", "message": "Ingestion started in background"}


def run_ingestion_background(file_key: str):
    print(f"🔄 [BACKGROUND] Starting ingestion logic for: {file_key}")
    try:
        s3 = boto3.client('s3')
        local_path = os.path.join(DATA_DIR, os.path.basename(file_key))

        print(f"⬇️ Downloading {file_key} from S3...")
        s3.download_file(S3_BUCKET_NAME, file_key, local_path)

        print("🚀 Launching ingest.py subprocess...")
        process = subprocess.Popen(
            ["python", "ingest.py"],
            stdout=sys.stdout,  # direct logs on CloudWatch
            stderr=sys.stderr,
            text=True
        )
        process.wait()  # no problem here, it's background task
        print(f"✅ Subprocess finished with code {process.returncode}")

    except Exception as e:
        print(f"💀 Critical Background Error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Note: Port 8002 internal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from retriever import Retriever
from generator import Generator
from constants import NUM_DOCS, DATA_DIR, S3_BUCKET_NAME
import subprocess
import boto3
import os

app = FastAPI()

print("Initializing RAG Service...")
retriever = Retriever(num_docs=NUM_DOCS)
generator = Generator()


class RAGRequest(BaseModel):
    query: str


class RAGResponse(BaseModel):
    answer: str
    context_used: str  # Optional: debug mode


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


class IngestRequest(BaseModel):
    file_key: str  # Il nome del file su S3 (es. "documenti/paper.pdf")


@app.post("/ingest-s3")
def ingest_from_s3(request: IngestRequest):
    print(f"📥 Received ingestion request for: {request.file_key}")

    try:
        s3 = boto3.client('s3')
        local_path = os.path.join(DATA_DIR, os.path.basename(request.file_key))
        print(f"Downloading from bucket {S3_BUCKET_NAME} to {local_path}...")
        s3.download_file(S3_BUCKET_NAME, request.file_key, local_path)

        # Starting the script as an imported module might cause an memory leak over time
        print("Running ingestion script...")
        result = subprocess.run(["python", "ingest.py"], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Ingestion failed: {result.stderr}")
            raise Exception(result.stderr)

        print(f"✅ Ingestion success: {result.stdout}")
        return {"status": "success", "message": f"Ingested {request.file_key}"}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Note: Port 8002 internal

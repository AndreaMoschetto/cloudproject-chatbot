# orchestrator/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_repository
import httpx
from constants import RAG_SERVICE_URL

app = FastAPI()

db = get_repository()


class QueryRequest(BaseModel):
    query: str
    session_id: str


class QueryResponse(BaseModel):
    answer: str


class IngestRequest(BaseModel):
    file_key: str


@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):  # Ora è async perché usiamo httpx
    try:
        db.save_message(request.session_id, "user", request.query)

        # Call RAG service
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{RAG_SERVICE_URL}/generate",
                json={"query": request.query}
            )
            response.raise_for_status()
            rag_data = response.json()
            answer = rag_data["answer"]

        db.save_message(request.session_id, "assistant", answer)

        return QueryResponse(answer=answer)

    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="RAG Service unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{session_id}")
def get_chat_history(session_id: str):
    try:
        return db.get_history(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest-s3")
async def trigger_ingestion(request: IngestRequest):
    print(f"Orchestrator received ingestion trigger for: {request.file_key}")
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:  # Longer timeout for ingestion
            response = await client.post(
                f"{RAG_SERVICE_URL}/ingest-s3",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        print(f"Error forwarding to RAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))

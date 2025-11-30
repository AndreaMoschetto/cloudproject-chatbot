from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from retriever import Retriever
from generator import Generator
from constants import NUM_DOCS

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Note: Port 8002 internal

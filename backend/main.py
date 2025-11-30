from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from generator import Generator
from retriever import Retriever
import uvicorn
from constants import NUM_DOCS
from database import get_repository
# import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument("--num_docs", type=int, default=5, help="Number of documents to retrieve")
# args = parser.parse_args()

app = FastAPI()
db = get_repository()
retriever = Retriever(num_docs=NUM_DOCS)
generator = Generator()


class QueryRequest(BaseModel):
    query: str
    session_id: str = "default_session"


class QueryResponse(BaseModel):
    answer: str


@app.post("/query", response_model=QueryResponse)
def generate_answer(request: QueryRequest):
    try:
        db.save_message(request.session_id, "user", request.query)

        context = retriever.get_context(request.query)
        answer = generator.generate_answer(request.query, context)

        db.save_message(request.session_id, "assistant", answer)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)

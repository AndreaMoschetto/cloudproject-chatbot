from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from generator import Generator
from retriever import Retriever
import uvicorn


app = FastAPI()
retriever = Retriever()
generator = Generator()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str


@app.post("/query", response_model=QueryResponse)
def generate_answer(request: QueryRequest):
    try:
        context = retriever.get_context(request.query)
        answer = generator.generate_answer(request.query, context)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)

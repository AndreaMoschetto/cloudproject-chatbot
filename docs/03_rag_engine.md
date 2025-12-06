# 3. The RAG Engine (Retrieval-Augmented Generation)

The intelligent heart of the platform is the **RAG** engine, which combines semantic search capability on private documents with the generative power of Large Language Models (LLMs).

The implementation in CloudNLP surpasses the limitations of basic tutorials by adopting a robust architecture suitable for a concurrent containerized environment.

## Key Components

### 1. Vector Store: ChromaDB (Client/Server Architecture)
Initially designed to use a local library, the system was migrated towards a **ChromaDB Client/Server** architecture to solve critical concurrency issues (file locking) when multiple processes (Ingestion and Retrieval) attempted to access the database on disk simultaneously.

* **Chroma Server:** Runs as an independent container (sidecar) in the backend task. Manages disk persistence and vector read/write operations. Exposes an internal API on port 8000.
* **Chroma Clients:** The `rag-service` services (both the API process and ingestion subprocesses) use `chromadb.HttpClient` to communicate with the server via TCP (`localhost:8000`), ensuring thread-safe and performant operations.

### 2. Embeddings: HuggingFace
Text transformation into numerical vectors (embeddings) is entrusted to the `all-MiniLM-L6-v2` model via the `langchain-huggingface` library.
* This model was chosen for its excellent balance between inference speed (crucial on Fargate CPU) and semantic representation quality.
* The model is downloaded and cached inside the RAG container at startup.

### 3. LLM: Google Gemini Pro
Response generation is delegated to Google's **Gemini Pro** model, accessible via API.
* **LangChain Integration:** We use `ChatGoogleGenerativeAI` from LangChain to abstract API calls.
* **Prompt Engineering:** A specific template instructs the model to behave as a technical assistant, requiring it to answer *exclusively* based on the provided context ("based *only* on the following context") to minimize hallucinations.

## The RAG Flow

### Phase 1: Retrieval (The "Retriever")
When the user asks a question:
1.  The query is converted into an embedding by the same HuggingFace model.
2.  A semantic similarity search (cosine similarity) is performed on ChromaDB.
3.  The system retrieves the `k` (default 5) most relevant text "chunks" relative to the question.

### Phase 2: Generation (The "Generator")
1.  The retrieved chunks are concatenated to form the "Context".
2.  The Prompt is constructed by combining: System Instructions + Context + User Question.
3.  The complete Prompt is sent to Gemini Pro.
4.  The generated answer is returned to the user, along with the sources used (for transparency).
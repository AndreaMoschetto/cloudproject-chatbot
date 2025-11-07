# 📄 RAG PDF Chatbot

This is an elementary Retrieval-Augmented Generation (RAG) project that allows you to chat with your PDF documents.

It's built with a modern, decoupled microservice architecture: a powerful **FastAPI** backend that handles all the NLP logic and a lightweight **Chainlit** frontend for a clean, interactive chat UI.

### 🚀 Core Architecture

  * **Backend (`main.py`):** A FastAPI server that loads the models and exposes a single `/query` endpoint. It uses the `Retriever` and `Generator` classes to handle all logic.
  * **Frontend (`app.py`):** A standalone Chainlit app that provides the user interface. It makes HTTP requests to the FastAPI backend and streams the response.
  * **Ingestor (`ing.py`):** A script to process your local PDFs, turn them into vectors, and store them in a local `ChromaDB` database.
  * **PDF Parsing:** Uses `pymupdf` for fast and accurate text/Markdown extraction from PDFs.
  * **Core Logic:** `LangChain` is used for orchestration, `HuggingFace` models for embeddings, and the **Google Gemini API** for generation.

-----

### 🏁 How to Use

#### Step 1: Setup

1.  **Clone the Repository:**

    ```bash
    git clone <your-repo-url>
    cd RAG
    ```

2.  **Create Your Environment File:**
    Create a file named `.env` in the root of the project. This is where you'll store your Google API key.

    ```ini
    GOOGLE_API_KEY="your_gemini_api_key_here"
    ```

3.  **Install Dependencies (Using `environment.yml`):**
    This project uses `conda` and includes a complete `environment.yml` file to ensure all dependencies are correct.

    ```bash
    # 1. Create the conda environment from the file
    conda env create -f environment.yml

    # 2. Activate the new environment
    conda activate rag_project
    ```

    This file handles all `conda` and `pip` dependencies automatically.

#### Step 2: Add Your Data

1.  Place any PDF files you want to chat with inside the `/data` folder.
      * `data/paper.pdf`
      * `data/riassunto.pdf`

#### Step 3: Ingest Documents

You must run the ingestion script *first* to build the vector database. Make sure your `rag_project` environment is active.

```bash
python ingest.py
```

  * **Customize Chunking (Optional):**
    You can control the text chunking strategy using command-line arguments:
    ```bash
    # Create 1000-character chunks with a 100-character overlap
    python ingest.py --size 1000 --overlap 100
    ```
      * `--size`: The target size for each text chunk (default: 3000).
      * `--overlap`: The amount of text to overlap between chunks (default: 200).

#### Step 4: Run the Application (2 Terminals)

This application runs as two separate services. You'll need two terminals (both with the `rag_project` environment active).

**In Terminal 1: Run the Backend (FastAPI)**

```bash
python main.py
```

  * **Customize Retrieval (Optional):**
    You can control how many documents the retriever fetches:
    ```bash
    # Retrieve the top 3 documents for context
    python main.py --num_docs 3
    ```

**In Terminal 2: Run the Frontend (Chainlit)**

```bash
# We must use a different port, since 8000 is taken by the backend
chainlit run app.py -w --port 8001
```

#### Step 5: Chat\!

Open your browser to **`http://localhost:8001`** to start chatting with your documents.
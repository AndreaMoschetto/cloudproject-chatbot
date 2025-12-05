import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from constants import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL_NAME, CHROMA_SERVER_HOST, CHROMA_SERVER_PORT


def get_chroma_client():
    """Factory: Restituisce un HttpClient se configurato, altrimenti PersistentClient"""
    if CHROMA_SERVER_HOST and CHROMA_SERVER_PORT:
        print(f"🔌 Connecting to ChromaDB Server at {CHROMA_SERVER_HOST}:{CHROMA_SERVER_PORT}")
        # In modalità server, non usiamo path locale
        return chromadb.HttpClient(host=CHROMA_SERVER_HOST, port=CHROMA_SERVER_PORT)
    else:
        print(f"📂 Connecting to local vector store at {CHROMA_DIR}")
        return chromadb.PersistentClient(path=CHROMA_DIR)


class Retriever:
    def __init__(self, num_docs: int = 5):
        print("Initializing embedding function (Heavy Model)...")
        self.embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        self.num_docs = num_docs

    def get_context(self, query: str) -> str:
        # Otteniamo il client corretto (Server o Locale)
        client = get_chroma_client()

        vector_store = Chroma(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding_function=self.embedding_function,
        )

        retriever = vector_store.as_retriever(search_kwargs={"k": self.num_docs})

        print(f"🔎 Retrieving docs for: {query}")
        try:
            retrieved_docs = retriever.invoke(query)
            formatted_context = "\n\n---\n\n".join(doc.page_content for doc in retrieved_docs)
            return formatted_context
        except Exception as e:
            print(f"❌ Error retrieving docs: {e}")
            return ""

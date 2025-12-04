import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from constants import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL_NAME


class Retriever:
    def __init__(self, num_docs: int = 5):
        print("Initializing embedding function (Heavy Model)...")
        self.embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        self.num_docs = num_docs
        print("Retriever initialized. DB connection will be lazy-loaded.")

    def get_context(self, query: str) -> str:
        print(f"🔄 Re-connecting to vector store at: {CHROMA_DIR}")

        try:
            # This avoids "Nothing found on disk" errors when ingestion updates files while the API is running.
            fresh_client = chromadb.PersistentClient(path=CHROMA_DIR)

            vector_store = Chroma(
                client=fresh_client,
                collection_name=COLLECTION_NAME,
                embedding_function=self.embedding_function,
            )

            # on-the-fly we create a retriever
            retriever = vector_store.as_retriever(search_kwargs={"k": self.num_docs})

            print(f"🔎 Retrieving docs for: {query}")
            retrieved_docs = retriever.invoke(query)

            if not retrieved_docs:
                print("⚠️ No documents found in the database.")
                return ""

            print(f"✅ Found {len(retrieved_docs)} documents.")

            formatted_context = "\n\n---\n\n".join(doc.page_content for doc in retrieved_docs)
            return formatted_context

        except Exception as e:
            print(f"❌ Critical Error accessing Vector DB: {e}")
            return ""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from constants import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL_NAME


class Retriever:
    def __init__(self):
        print("Initializing embedding function...")
        self.embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

        print(f"Loading vector store from: {CHROMA_DIR}")
        self.vector_store = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=self.embedding_function,
            collection_name=COLLECTION_NAME
        )
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        print("Retriever initialized.")

    def get_context(self, query: str) -> str:
        retrieved_docs = self.retriever.invoke(query)
        formatted_context = "\n\n---\n\n".join(doc.page_content for doc in retrieved_docs)
        return formatted_context

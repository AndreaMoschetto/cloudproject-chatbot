import os
import pymupdf4llm as pymu
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

_DATA_DIR = "data/"
_CHROMA_DIR = "chroma_db/"
_EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
_COLLECTION_NAME = "my_course_notes"

print("Initializing embedding function...")
embedding_function = HuggingFaceEmbeddings(model_name=_EMBEDDING_MODEL_NAME)
print(f"Loading PDF from {_DATA_DIR} and converting to markdown...")

all_chunks = []
processed_files = 0
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,  # Overlap helps keep context between chunks
    length_function=len
)

for filename in os.listdir(_DATA_DIR):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(_DATA_DIR, filename)
        print(f"Processing {pdf_path}...")
        try:
            md_text = pymu.to_markdown(pdf_path)
            chunks = splitter.split_text(md_text)
            for i, chunk in enumerate(chunks):
                all_chunks.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "source": filename,
                            "chunk_index": i
                        }
                    )
                )
            processed_files += 1
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")

if not all_chunks:
    print("No documents were successfully processed. Exiting.")
    exit()

print(f"\nProcessed {processed_files} files, {len(all_chunks)} total chunks.")

print("Creating and persisting vector store...")
vector_store = Chroma.from_documents(
    documents=all_chunks,
    embedding=embedding_function,
    persist_directory=_CHROMA_DIR,
    collection_name=_COLLECTION_NAME
)
print(f"✅ Ingestion complete! Vector store saved to {_CHROMA_DIR}")

import os
import argparse
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
import pymupdf4llm as pymu
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from constants import DATA_DIR, CHROMA_DIR, EMBEDDING_MODEL_NAME, COLLECTION_NAME

parser = argparse.ArgumentParser()
parser.add_argument('--size', type=int, default=3000, help='Size of each text chunk')
parser.add_argument('--overlap', type=int, default=200, help='Size of each text chunk overlap')
args = parser.parse_args()

print("Initializing embedding function...")
embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

print(f"Loading PDF from {DATA_DIR}...")

all_chunks = []
processed_files = 0
splitter = RecursiveCharacterTextSplitter(
    chunk_size=args.size,
    chunk_overlap=args.overlap,
    length_function=len
)

for filename in os.listdir(DATA_DIR):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(DATA_DIR, filename)
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

print(f"Connecting to vector store at {CHROMA_DIR}...")

# Instead of using Chroma.from_documents (which resets/creates), we use the Persistent Client.
# This ensures we write in the same way the Retriever reads.
client = chromadb.PersistentClient(path=CHROMA_DIR)

vector_store = Chroma(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding_function=embedding_function,
)

print("Adding documents to vector store...")

# We don't want to overwrite existing data, so we use add_documents
vector_store.add_documents(documents=all_chunks)

print(f"✅ Ingestion complete! Vector store updated at {CHROMA_DIR}")

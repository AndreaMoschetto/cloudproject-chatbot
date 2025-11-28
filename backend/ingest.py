import os
from langchain_huggingface import HuggingFaceEmbeddings
import pymupdf4llm as pymu
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from constants import DATA_DIR, CHROMA_DIR, EMBEDDING_MODEL_NAME, COLLECTION_NAME
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--size', type=int, default=3000, help='Size of each text chunk')
parser.add_argument('--overlap', type=int, default=200, help='Size of each text chunk overlap')
args = parser.parse_args()

print("Initializing embedding function...")
embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

print(f"Loading PDF from {DATA_DIR} and converting to markdown...")

all_chunks = []
processed_files = 0
splitter = RecursiveCharacterTextSplitter(
    chunk_size=args.size,
    chunk_overlap=args.overlap,  # Overlap helps keep context between chunks
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

print("Creating and persisting vector store...")
vector_store = Chroma.from_documents(
    documents=all_chunks,
    embedding=embedding_function,
    persist_directory=CHROMA_DIR,
    collection_name=COLLECTION_NAME
)
print(f"✅ Ingestion complete! Vector store saved to {CHROMA_DIR}")

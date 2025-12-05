import os
import argparse
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
import pymupdf4llm as pymu
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from constants import (
    DATA_DIR, CHROMA_DIR, EMBEDDING_MODEL_NAME, COLLECTION_NAME,
    CHROMA_SERVER_HOST, CHROMA_SERVER_PORT
)

parser = argparse.ArgumentParser()
parser.add_argument('--size', type=int, default=3000, help='Size of each text chunk')
parser.add_argument('--overlap', type=int, default=200, help='Size of each text chunk overlap')
parser.add_argument('--file', type=str, default=None, help="Specific file to process (optional)")
args = parser.parse_args()

print("Initializing embedding function...")
embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

print(f"Loading {args.file if args.file else 'all PDFs'} from {DATA_DIR}...")

files_to_process = []
if args.file:
    # Se c'è l'argomento, processiamo SOLO questo file
    file_path = os.path.join(DATA_DIR, args.file)
    if os.path.exists(file_path):
        files_to_process.append(args.file)
    else:
        print(f"⚠️ File {args.file} not found in {DATA_DIR}. Skipping.")
        exit()
else:
    print(f"Scanning {DATA_DIR}...")
    files_to_process = [f for f in os.listdir(DATA_DIR) if f.endswith(".pdf")]

if not files_to_process:
    print("No files to process.")
    exit()


all_chunks = []
processed_files = 0
splitter = RecursiveCharacterTextSplitter(
    chunk_size=args.size,
    chunk_overlap=args.overlap,
    length_function=len
)

for filename in files_to_process:
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

print("Connecting to vector store...")

if CHROMA_SERVER_HOST and CHROMA_SERVER_PORT:
    print(f"🔌 Connecting to ChromaDB Server at {CHROMA_SERVER_HOST}:{CHROMA_SERVER_PORT}")
    client = chromadb.HttpClient(host=CHROMA_SERVER_HOST, port=CHROMA_SERVER_PORT)
else:
    print(f"📂 Connecting to local vector store at {CHROMA_DIR}")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

vector_store = Chroma(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding_function=embedding_function,
)


if all_chunks:
    print(f"Adding {len(all_chunks)} chunks to vector store...")
    vector_store.add_documents(documents=all_chunks)
    print(f"✅ Ingestion complete for: {files_to_process}")
else:
    print("No chunks generated.")

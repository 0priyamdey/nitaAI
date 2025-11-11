import os
import glob
import shutil
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Configuration (Filled In) ---
# Read from the output of our other scripts
TEXT_DATA_DIRS = ["../data/web_text", "../data/pdf_text"]

# Chunking parameters from the proposal [8, 1]
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Embedding model from the proposal [3, 4, 1]
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Database path (inside the backend folder)
PERSIST_DIRECTORY = '../backend/db'

# --- Loading Logic ---
print("Loading ingested text data...")
all_docs = []

for data_dir in TEXT_DATA_DIRS:
    print(f"--- Loading from: {data_dir} ---")
    text_files = glob.glob(os.path.join(data_dir, "*.txt"))
    
    if not text_files:
        print(f"Warning: No.txt files found in {data_dir}")
        continue
        
    for text_file in text_files:
        with open(text_file, "r", encoding="utf-8") as f:
            # First line is metadata (e.g., "Source URL:...")
            source_line = f.readline().strip()
            content = f.read()
            
            # Use the first line as the 'source' metadata
            source_id = source_line.split(":", 1)[-1].strip()
            
            # Create a Document object
            doc = Document(page_content=content, metadata={"source": source_id})
            all_docs.append(doc)

print(f"\nLoaded {len(all_docs)} raw documents.")

if not all_docs:
    print("No documents found to process. Halting build.")
    print("Please add PDFs to 'data/pdfs' and configure/run 'ingest_web.py'.")
    exit()

# --- Chunking Logic ---
print("Chunking documents...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    is_separator_regex=False,
    separators=["\n\n", "\n", ". ", " ", ""] # [8]
)

split_documents = text_splitter.split_documents(all_docs)
print(f"Created {len(split_documents)} text chunks.")

# --- Embedding Model Logic ---
print(f"Loading embedding model: '{EMBEDDING_MODEL}'...")
model_kwargs = {'device': 'cpu'} 
encode_kwargs = {'normalize_embeddings': False}

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
) [3, 4]
print("Embedding model loaded.")

# --- Vector Store Logic ---
if os.path.exists(PERSIST_DIRECTORY):
    print(f"Cleaning up old database at '{PERSIST_DIRECTORY}'...")
    shutil.rmtree(PERSIST_DIRECTORY)

print(f"Building persistent ChromaDB in '{PERSIST_DIRECTORY}'...")

# This command builds the entire vector database [9, 10]
db = Chroma.from_documents(
    documents=split_documents, 
    embedding=embeddings, 
    persist_directory=PERSIST_DIRECTORY
)

print("\n-------------------------------------------------")
print("Vector database built successfully.")
print(f"Total chunks indexed: {len(split_documents)}")
print(f"Database location: {PERSIST_DIRECTORY}")
print("-------------------------------------------------")
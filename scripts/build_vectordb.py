from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
import glob

# --- Configuration ---
TEXT_DATA_DIRS = ["data/web_text", "data/pdf_text"]
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# --- Loading Logic ---
print("Loading ingested text data...")
all_texts =[]
all_metadatas =[]

for data_dir in TEXT_DATA_DIRS:
    text_files = glob.glob(os.path.join(data_dir, "*.txt"))
    for text_file in text_files:
        with open(text_file, "r", encoding="utf-8") as f:
            # First line is metadata (e.g., "Source URL:...")
            source_line = f.readline().strip()
            content = f.read()
            
            source_id = source_line.split(":", 1)[-1].strip()
            
            all_texts.append(content)
            all_metadatas.append({"source": source_id})

print(f"Loaded {len(all_texts)} raw documents.")

# --- Chunking Logic ---
# Instantiate the recursive splitter [8]
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    is_separator_regex=False,
    separators=["\n\n", "\n", ". ", " ", ""] # Separators 
)

# Create Document objects with metadata
# This is a more efficient way to create documents
documents = text_splitter.create_documents(all_texts, metadatas=all_metadatas)

print(f"Created {len(documents)} text chunks.")

# 'documents' is now a list of Document objects, ready for embedding.

# (This code follows the code from Section 1.3, in the same file)
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- Embedding Model Logic ---
print("Loading embedding model 'all-MiniLM-L6-v2'...")

# This is the wrapper for the 'all-MiniLM-L6-v2' model [24]
model_name = "sentence-transformers/all-MiniLM-L6-v2"

# Configure model to run on CPU. Change to 'cuda' for GPU.
model_kwargs = {'device': 'cpu'} 

# 'normalize_embeddings' is set to False for ChromaDB compatibility
encode_kwargs = {'normalize_embeddings': False}

embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

print("Embedding model loaded successfully.")


# (This code follows the code from Section 2.2, in the same file)
from langchain_community.vectorstores import Chroma
import shutil

# --- Vector Store Logic ---
# Define the path for the persistent database
persist_directory = 'db'

# Optional: Clean up old database directory
if os.path.exists(persist_directory):
    print(f"Cleaning up old database at '{persist_directory}'...")
    shutil.rmtree(persist_directory)

print(f"Building persistent ChromaDB in '{persist_directory}'...")

# This single command builds the entire vector database:
# 1. Takes all 'documents' (chunks)
# 2. Passes each one to the 'embeddings' function
# 3. Stores the resulting vectors in ChromaDB
# 4. Persists the database to the './db' directory 
db = Chroma.from_documents(
    documents=documents, 
    embedding=embeddings, 
    persist_directory=persist_directory
)

print("-------------------------------------------------")
print("Vector database built successfully.")
print(f"Total documents indexed: {len(documents)}")
print(f"Database location: {persist_directory}")
print("-------------------------------------------------")
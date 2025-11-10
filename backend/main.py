import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

# --- 1. Initialize AI Components (on startup) ---
print("Loading AI components...")
# (Reuse code from 3.1 and 3.2)
# --- (omitted for brevity) ---
model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'device': 'cpu'})
db = Chroma(persist_directory="db", embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={"k": 3})
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# 5. Create the final RAG Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True  # Include source docs in the result 
)
print("AI components loaded successfully.")

# --- 2. Define FastAPI App ---
app = FastAPI(title="NITai Project API")

# Set up CORS (Cross-Origin Resource Sharing) [30, 31]
origins =[]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],
)

# --- 3. Define API Data Models ---
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    source: str

# --- 4. Define API Endpoint ---
@app.post("/api/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Handles a user query by passing it through the RAG chain.
    """
    print(f"Received query: {request.query}")
    
    try:
        # Run the query through the RAG chain
        result = qa_chain.invoke({"query": request.query})
        
        # Format the response
        answer = result.get("result", "Sorry, I couldn't find an answer.")
        
        # Extract the first source for citation
        first_source = "No source found"
        if result.get("source_documents"):
            first_source = result["source_documents"].metadata.get("source", "Unknown")

        return QueryResponse(
            answer=answer,
            source=first_source
        )
    except Exception as e:
        print(f"Error processing query: {e}")
        return QueryResponse(
            answer="An error occurred while processing the request.",
            source="Error"
        )

@app.get("/api/health", tags=["Monitoring"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}

# --- 5. Run the server ---
# To run: `pip install "fastapi[all]" uvicorn "langchain[all]" langchain-openai chromadb sentence-transformers`
# Then:   `uvicorn main:app --reload`
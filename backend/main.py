# main.py (lazy-import safe)
import os
import asyncio
from typing import Optional, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Do NOT import langchain_community or langchain_core at module import time.
# We'll lazy-import them inside initializer to avoid import-time failures.

load_dotenv()

# ---- Configuration ----
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIR", "db")
RETRIEVE_K = int(os.getenv("RETRIEVE_K", "4"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0"))
# ------------------------

# Placeholders to be initialized lazily
embeddings = None
vectordb = None
retriever = None

_llm_instance = None  # langchain_openai wrapper instance cache


# --- Lazy init for vectorstore & embeddings ---
def init_vectorstore_and_embeddings():
    global embeddings, vectordb, retriever
    if retriever is not None:
        return True

    try:
        # Lazy imports (may raise if packages have incompatible deps)
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import Chroma
    except Exception as e:
        # Report a friendly error; do NOT raise raw to avoid crashing app import.
        print("Could not import langchain_community vectorstore/embeddings:", repr(e))
        print("If you need vector DB functionality, install compatible langchain_community/langchain_core/langsmith packages or use fallback storage.")
        return False

    try:
        model_kwargs = {"device": EMBEDDING_DEVICE}
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME, model_kwargs=model_kwargs)
        vectordb = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
        retriever = vectordb.as_retriever(search_kwargs={"k": RETRIEVE_K})
        print("Vectorstore and embeddings initialized (Chroma + HuggingFace).")
        return True
    except Exception as e:
        print("Error initializing Chroma/HuggingFaceEmbeddings:", repr(e))
        return False


# --- Lazy LLM init with langchain_openai fallback to openai SDK ---
def _init_llm():
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance
    try:
        # try LangChain wrapper (lazy)
        from langchain_openai import ChatOpenAI as LCChatOpenAI
        _llm_instance = LCChatOpenAI(model_name=OPENAI_MODEL, temperature=OPENAI_TEMPERATURE)
        print("Using langchain_openai.ChatOpenAI")
        return _llm_instance
    except Exception as e:
        print("langchain_openai not usable (falling back to openai SDK):", repr(e))
        _llm_instance = None
        return None


def _call_llm_with_prompt(prompt_text: str) -> str:
    # 1) Try LangChain wrapper
    lc = _init_llm()
    if lc is not None:
        try:
            return lc.predict(prompt_text)
        except Exception:
            try:
                res = lc.__call__([{"role": "user", "content": prompt_text}])
                if hasattr(res, "text"):
                    return res.text
                if hasattr(res, "generations"):
                    gens = getattr(res, "generations", None)
                    try:
                        first = gens[0][0]
                        return getattr(first, "text", str(first))
                    except Exception:
                        pass
                return str(res)
            except Exception as e:
                print("LangChain wrapper call failed, will fallback to OpenAI SDK:", repr(e))
                # fall through to SDK

    # 2) Fallback: openai SDK
    try:
        import openai

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key

        messages = [{"role": "user", "content": prompt_text}]
        completion = openai.ChatCompletion.create(model=OPENAI_MODEL, messages=messages, temperature=OPENAI_TEMPERATURE)
        if completion and getattr(completion, "choices", None):
            choice = completion.choices[0]
            # modern shape: choice.message.content
            msg = getattr(choice, "message", None)
            if isinstance(msg, dict):
                content = msg.get("content")
                if content:
                    return content
            elif msg is not None:
                content = getattr(msg, "content", None)
                if content:
                    return content
            # fallback to choice.text
            if getattr(choice, "text", None):
                return choice.text
        return str(completion)
    except Exception as e:
        raise RuntimeError("LLM invocation failed (both langchain wrapper and openai SDK). Check OPENAI_API_KEY and packages.") from e


# --- Retrieval + answer helper ---
def answer_with_retrieval(query: str, k: int = RETRIEVE_K) -> dict:
    """
    Attempt to initialize vectorstore lazily and answer the query.
    If vectorstore is unavailable, returns an informative error message.
    """
    ok = init_vectorstore_and_embeddings()
    if not ok or retriever is None:
        # Vector DB not available — return a helpful response
        return {
            "answer": "Vector DB is not available on this server. Check logs for langchain_community/langsmith compatibility or install required packages.",
            "sources": [],
        }

    # ensure k
    try:
        retriever.search_kwargs = {"k": k}
    except Exception:
        pass

    docs = retriever.get_relevant_documents(query)

    context_pieces: List[str] = []
    sources: List[str] = []
    for d in docs:
        text = getattr(d, "page_content", None) or getattr(d, "text", None) or ""
        if text:
            context_pieces.append(text)
        meta = getattr(d, "metadata", {}) or {}
        source = meta.get("source") or meta.get("file") or meta.get("source_id") or None
        if source:
            sources.append(source)

    context = "\n\n".join(context_pieces) if context_pieces else "(no context found)"

    prompt = (
        "You are an expert assistant for the National Institute of Technology, Agartala.\n"
        "Use the following pieces of retrieved context to answer the question concisely.\n"
        "If the answer is not present in the context, say that you don't know.\n\n"
        "Context:\n"
        f"{context}\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )

    answer_text = _call_llm_with_prompt(prompt)
    return {"answer": answer_text, "sources": sources}


# --- FastAPI app & CORS ---
app = FastAPI(title="NITai Project API")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    source: Optional[str] = None


@app.post("/api/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    query = request.query
    print("Received query:", query)
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, answer_with_retrieval, query, RETRIEVE_K)
        answer = result.get("answer", "Sorry, I couldn't find an answer.")
        sources = result.get("sources", [])
        first_source = sources[0] if sources else "No source found"
        return QueryResponse(answer=answer, source=first_source)
    except Exception as e:
        print("Error processing query:", repr(e))
        return QueryResponse(answer="An error occurred while processing the request.", source="Error")

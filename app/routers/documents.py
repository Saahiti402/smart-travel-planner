import os
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# =========================
# CONFIG
# =========================
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = Path(os.getenv("RAG_DATA_PATH", str(BASE_DIR / "RAG_Data")))
VECTOR_DB_PATH = Path(os.getenv("RAG_VECTOR_DB_PATH", str(BASE_DIR / "vector_store")))

router = APIRouter(prefix="/rag", tags=["Documents & RAG"])

vector_db = None
embeddings = None


# =========================
# SCHEMAS (INLINE)
# =========================
class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


class QueryResponse(BaseModel):
    results: List[str]


class LoadResponse(BaseModel):
    message: str
    total_chunks: int


# =========================
# INTERNAL FUNCTIONS
# =========================

def get_embeddings():
    global embeddings

    if embeddings is None:
        embeddings = OpenAIEmbeddings()

    return embeddings


def load_documents():
    documents = []

    if not DATA_PATH.exists():
        raise Exception(f"RAG data folder not found: {DATA_PATH}")

    for file_path in sorted(DATA_PATH.glob("*.txt")):
        if file_path.is_file():
            loader = TextLoader(str(file_path), encoding="utf-8")
            documents.extend(loader.load())

    if not documents:
        raise Exception(f"No .txt files found in {DATA_PATH}")

    return documents


def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_documents(docs)


def build_vector_store():
    global vector_db

    docs = load_documents()
    chunks = split_documents(docs)

    vector_db = FAISS.from_documents(chunks, get_embeddings())
    vector_db.save_local(str(VECTOR_DB_PATH))

    return len(chunks)


def load_vector_store():
    global vector_db

    if VECTOR_DB_PATH.exists():
        vector_db = FAISS.load_local(
            str(VECTOR_DB_PATH),
            get_embeddings(),
            allow_dangerous_deserialization=True
        )
    else:
        raise Exception("Vector DB not found. Call /rag/load first.")


def query_vector_store(query, top_k):
    global vector_db

    if vector_db is None:
        load_vector_store()

    docs = vector_db.similarity_search(query, k=top_k)

    return [doc.page_content for doc in docs]


# =========================
# ENDPOINTS
# =========================

# 🔹 Load all backend documents into vector DB
@router.post("/load", response_model=LoadResponse)
def load_rag_documents():
    try:
        total_chunks = build_vector_store()

        return {
            "message": "RAG documents loaded successfully",
            "total_chunks": total_chunks
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 Query RAG
@router.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    try:
        results = query_vector_store(request.query, request.top_k)

        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 Health check
@router.get("/health")
def health():
    return {"status": "Documents & RAG service running"}

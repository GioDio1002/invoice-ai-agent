"""RAG: FAISS vector store and retriever for historical invoices/POs/receipts."""

import os
from pathlib import Path
from typing import Optional

# Lazy imports to avoid loading heavy deps when RAG not used

_FAISS_INDEX_PATH = Path(os.getenv("FAISS_INDEX_PATH", "faiss_index"))
_global_store = None


def _get_embeddings():
    """OpenAI or HuggingFace embeddings (OpenAI if key set)."""
    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model="text-embedding-3-small")
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )
    except ImportError:
        from langchain_community.embeddings import FakeEmbeddings
        return FakeEmbeddings(size=384)


def get_vector_store(force_new: bool = False):
    """Return a FAISS index (in-memory or load from disk). Creates empty if none."""
    global _global_store
    if _global_store is not None and not force_new:
        return _global_store
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document

    embeddings = _get_embeddings()
    index_faiss = _FAISS_INDEX_PATH / "index.faiss"
    if index_faiss.exists() and not force_new:
        try:
            _global_store = FAISS.load_local(str(_FAISS_INDEX_PATH), embeddings, allow_dangerous_deserialization=True)
            return _global_store
        except Exception:
            pass
    # Empty store
    _global_store = FAISS.from_documents([Document(page_content="No documents yet.")], embeddings)
    return _global_store


def add_documents_to_rag(texts: list[str], metadatas: Optional[list[dict]] = None) -> None:
    """Add document chunks to FAISS. Call after invoice/PO/receipt processing."""
    from langchain_core.documents import Document

    store = get_vector_store()
    metas = metadatas or [{}] * len(texts)
    docs = [Document(page_content=t[:8000], metadata=metas[i]) for i, t in enumerate(texts)]
    store.add_documents(docs)
    _FAISS_INDEX_PATH.mkdir(parents=True, exist_ok=True)
    store.save_local(str(_FAISS_INDEX_PATH))


def get_retriever(k: int = 4):
    """Return a retriever over the FAISS store for use in agents."""
    return get_vector_store().as_retriever(search_kwargs={"k": k})

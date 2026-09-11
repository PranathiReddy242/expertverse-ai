from typing import Any
import numpy as np
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.embeddings import get_embedding

INDEX_DIM = 1536
_vectors: list[np.ndarray] = []
_metadata: list[dict[str, Any]] = []


def initialize_vector_store(db: Session):
    global _vectors, _metadata
    _vectors.clear()
    _metadata.clear()
    try:
        docs = db.query(Document).all()
        for doc in docs:
            if not doc.text:
                continue
            embedding = get_embedding(doc.text)
            _vectors.append(np.array(embedding, dtype=np.float32))
            _metadata.append({"expert_id": doc.expert_id, "document_id": doc.id, "text": doc.text})
    except Exception as e:
        print(f"Vector store init notice: {e}")


def add_documents_to_expert(expert_id: int, documents: list[dict[str, Any]]):
    global _vectors, _metadata
    for doc in documents:
        text = doc.get("text", "")
        if not text:
            continue
        embedding = np.array(get_embedding(text), dtype=np.float32)
        _vectors.append(embedding)
        _metadata.append({"expert_id": expert_id, "text": text, "file_type": doc.get("file_type")})


def query_expert_documents(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    if not _vectors or not _metadata:
        return []
    try:
        query_vec = np.array(get_embedding(query), dtype=np.float32)
        matrix = np.vstack(_vectors)
        # Compute cosine similarity / dot product with normalized vectors
        scores = np.dot(matrix, query_vec)
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if idx < len(_metadata):
                results.append({
                    "metadata": _metadata[idx],
                    "score": float(scores[idx]),
                })
        return results
    except Exception as e:
        print(f"Vector search notice: {e}")
        return []

from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.embeddings import get_embedding

DATA_DIR = Path(__file__).resolve().parent.parent.parent / ".faiss"
INDEX_DIM = 1536
index: faiss.IndexFlatL2 | None = None
metadata: list[dict[str, Any]] = []


def initialize_vector_store(db: Session):
    global index, metadata
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    metadata.clear()
    docs = db.query(Document).all()
    vectors = []
    for doc in docs:
        if not doc.text:
            continue
        embedding = get_embedding(doc.text)
        vectors.append(np.array(embedding, dtype=np.float32))
        metadata.append({"expert_id": doc.expert_id, "document_id": doc.id, "text": doc.text})
    index = faiss.IndexFlatL2(INDEX_DIM)
    if vectors:
        index.add(np.vstack(vectors))


def add_documents_to_expert(expert_id: int, documents: list[dict[str, Any]]):
    global index, metadata
    if index is None:
        index = faiss.IndexFlatL2(INDEX_DIM)
    for doc in documents:
        text = doc.get("text", "")
        if not text:
            continue
        embedding = np.array(get_embedding(text), dtype=np.float32)
        index.add(np.expand_dims(embedding, axis=0))
        metadata.append({"expert_id": expert_id, "text": text, "file_type": doc.get("file_type")})


def query_expert_documents(query: str, top_k: int = 5):
    if index is None or index.ntotal == 0:
        return []
    query_embedding = np.array(get_embedding(query), dtype=np.float32)
    distances, nearest = index.search(np.expand_dims(query_embedding, axis=0), top_k)
    results = []
    for idx, distance in zip(nearest[0], distances[0]):
        if idx < len(metadata):
            results.append({
                "metadata": metadata[idx],
                "score": float(distance),
            })
    return results

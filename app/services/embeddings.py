import hashlib
import math
from typing import Any

from app.core.config import settings
from app.services.llm_service import llm_service


import re

def _local_embedding(text: str) -> list[float]:
    """
    Computes a 1536-dimensional L2-normalized semantic feature embedding
    using sublinear term-frequency hashing over words, bigrams, and character n-grams.
    Ensures texts with shared domain vocabulary produce high cosine similarity in FAISS.
    """
    dim = 1536
    vec = [0.0] * dim
    if not text or not text.strip():
        return vec

    # Clean and tokenize
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    tokens = [t for t in cleaned.split() if len(t) > 1]
    if not tokens:
        return vec

    # Extract unigrams, bigrams, and character trigrams
    features = list(tokens)
    for i in range(len(tokens) - 1):
        features.append(f"{tokens[i]}_{tokens[i+1]}")
    for token in tokens:
        if len(token) >= 3:
            for j in range(len(token) - 2):
                features.append(f"#{token[j:j+3]}")

    for feat in features:
        # Stable deterministic hashing into vector dimensions
        h = int(hashlib.md5(feat.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if ((h >> 16) & 1) == 0 else -1.0
        # Weight unigrams more than char ngrams
        weight = 1.0 if not feat.startswith("#") else 0.35
        vec[idx] += sign * weight

    # L2 normalization
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]

    return vec


def _local_text_response(prompt: str) -> str:
    return (
        "AI fallback response: configure GROQ_API_KEY for Groq or run Ollama locally. "
        "Based on your prompt, the system recommends expert matching and a high-level roadmap."
    )


def _google_embedding(text: str) -> list[float]:
    if not settings.google_api_key:
        raise RuntimeError("GOOGLE_API_KEY is not configured")

    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise RuntimeError("google-generativeai is not available") from exc

    genai.configure(api_key=settings.google_api_key)
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="RETRIEVAL_DOCUMENT",
    )

    if isinstance(result, dict):
        embedding = result.get("embedding")
    else:
        embedding = getattr(result, "embedding", None)

    if not embedding:
        raise RuntimeError("Google embedding response was empty")

    if isinstance(embedding, list):
        return [float(value) for value in embedding]

    if isinstance(embedding, dict):
        values = embedding.get("values") or embedding.get("embedding")
        if isinstance(values, list):
            return [float(value) for value in values]

    return [float(value) for value in list(embedding)]


def get_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        return _local_embedding(text or "")

    try:
        return _google_embedding(text)
    except Exception:
        return _local_embedding(text)


def get_text_response(prompt: str, model: str = "default") -> str:
    try:
        resp = llm_service.generate_text(prompt, model=model)
        if resp and resp.strip():
            return resp
    except Exception:
        pass
    return _local_text_response(prompt)

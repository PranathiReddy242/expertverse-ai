from app.core.config import settings
import hashlib
import math
from app.services.llm_service import llm_service


def _local_embedding(text: str) -> list[float]:
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
    return [math.sin(seed + i) for i in range(1536)]


def _local_text_response(prompt: str) -> str:
    return (
        "AI fallback response: configure GROQ_API_KEY for Groq or run Ollama locally. "
        "Based on your prompt, the system recommends expert matching and a high-level roadmap."
    )


def get_embedding(text: str) -> list[float]:
    # For now use local embedding fallback; can integrate Groq/other services later
    return _local_embedding(text)


def get_text_response(prompt: str, model: str = "default") -> str:
    # Use centralized LLMService for text generation
    try:
        return llm_service.generate_text(prompt, model=model)
    except Exception:
        return _local_text_response(prompt)

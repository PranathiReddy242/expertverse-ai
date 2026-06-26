import logging
from typing import Optional

import requests
from app.core.config import settings

logger = logging.getLogger("llm_service")


class LLMService:
    def __init__(self):
        # Groq settings
        self.groq_key = settings.groq_api_key
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

        # Default model
        self.default_model = "llama-3.3-70b-versatile"

        # Ollama settings
        self.ollama_url = settings.ollama_url
        self.ollama_enabled = settings.ollama_enabled

        # System prompt
        self.system_prompt = """
You are ExpertVerse AI.

You are an intelligent AI career mentor and expert recommendation assistant.

Your responsibilities include:
- Answering career questions.
- Generating personalized learning roadmaps.
- Analyzing skills and identifying gaps.
- Suggesting mentors and experts.
- Providing professional and actionable advice.

Always provide structured, clear, and useful responses.
"""

    def _call_groq(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> Optional[str]:

        if not self.groq_key:
            logger.warning("No GROQ_API_KEY found")
            return None

        # Prevent model='default'
        if not model or model == "default":
            model = self.default_model

        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }

        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }

        try:

            response = requests.post(
                self.groq_url,
                json=payload,
                headers=headers,
                timeout=60
            )

            response.raise_for_status()

            data = response.json()

            if data.get("choices"):
                return (
                    data["choices"][0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )

            return None

        except Exception as e:
            logger.exception("Groq call failed: %s", e)
            return None

    def _call_ollama(
        self,
        prompt: str,
        model: str = "llama3.2"
    ) -> Optional[str]:

        if not self.ollama_enabled or not self.ollama_url:
            return None

        try:
            url = f"{self.ollama_url}/api/generate"

            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(
                url,
                json=payload,
                timeout=60
            )

            response.raise_for_status()

            data = response.json()

            if data.get("response"):
                return data["response"].strip()

            return None

        except Exception as e:
            logger.exception("Ollama call failed: %s", e)
            return None

    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> str:

        # Try Groq first
        output = self._call_groq(prompt, model)

        if output:
            logger.info("Using Groq provider")
            return output

        # Fallback to Ollama
        output = self._call_ollama(prompt)

        if output:
            logger.info("Using Ollama provider")
            return output

        logger.warning("No AI provider available")

        return (
            "Sorry, the AI service is temporarily unavailable. "
            "Please try again later."
        )


llm_service = LLMService()
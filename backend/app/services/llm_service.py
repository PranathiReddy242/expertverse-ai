import logging
from typing import Optional

import certifi
import requests
from requests.exceptions import SSLError
from app.core.config import settings

logger = logging.getLogger("llm_service")


class LLMService:
    def __init__(self):
        # Groq settings
        self.groq_key = settings.groq_api_key
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.groq_ca_bundle = settings.groq_ca_bundle
        self.groq_verify_ssl = settings.groq_verify_ssl

        # Default model
        self.default_model = "llama-3.3-70b-versatile"

        # Ollama settings
        self.ollama_url = settings.ollama_url
        self.ollama_enabled = settings.ollama_enabled

        # Google Gemini key
        self.google_key = settings.google_api_key

        # System prompt prioritizing clarity, ethical alignment, depth, and actionable guidance
        self.system_prompt = """You are ExpertVerse AI, a premier AI career mentor, technical advisor, and ethical AI strategist.

Core Directives:
1. Deliver comprehensive, clear, articulate, and direct answers to every user query.
2. Ground all advice in practical industry best practices and ethical standards (including transparency, fairness, privacy, safety, and sustainable career growth).
3. Provide actionable steps, explaining the 'why' and 'how' behind technical and strategic decisions.
4. Maintain an encouraging, empathetic, and professional tone that empowers the learner while promoting genuine mastery over shortcuts.
5. Emphasize how working with domain experts on ExpertVerse AI can accelerate their learning through personalized feedback, code reviews, and mentorship.
"""

    def _groq_verify_setting(self):
        if self.groq_ca_bundle:
            return self.groq_ca_bundle

        if not self.groq_verify_ssl:
            logger.warning("Groq SSL verification is disabled")
            return False

        return certifi.where()

    def _call_groq(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> Optional[str]:
        if not self.groq_key:
            return None

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
            "max_tokens": 1500
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
                timeout=45,
                verify=self._groq_verify_setting(),
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

        except SSLError as e:
            logger.warning(
                "Groq SSL verification failed: %s",
                e,
            )
            return None
        except Exception as e:
            logger.warning("Groq call failed: %s", e)
            return None

    def _call_gemini(self, prompt: str) -> Optional[str]:
        if not self.google_key:
            return None

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.google_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            full_prompt = f"{self.system_prompt}\n\nUser Question:\n{prompt}"
            resp = model.generate_content(full_prompt)
            if resp and resp.text:
                return resp.text.strip()
        except Exception as e:
            logger.warning("Gemini call failed: %s", e)
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
                "prompt": f"{self.system_prompt}\n\n{prompt}",
                "stream": False
            }
            response = requests.post(
                url,
                json=payload,
                timeout=45
            )
            response.raise_for_status()
            data = response.json()

            if data.get("response"):
                return data["response"].strip()
            return None

        except Exception as e:
            logger.warning("Ollama call failed: %s", e)
            return None

    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> Optional[str]:
        # 1. Try Groq first
        output = self._call_groq(prompt, model)
        if output:
            logger.info("Using Groq provider")
            return output

        # 2. Try Gemini
        output = self._call_gemini(prompt)
        if output:
            logger.info("Using Gemini provider")
            return output

        # 3. Fallback to Ollama
        output = self._call_ollama(prompt)
        if output:
            logger.info("Using Ollama provider")
            return output

        logger.info("No external LLM provider configured or reachable; using internal reasoning engine.")
        return None


llm_service = LLMService()

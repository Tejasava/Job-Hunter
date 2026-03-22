"""
Multi-LLM AI Router with Automatic Fallback System
Supports: Groq, Gemini, HuggingFace, OpenRouter, Ollama
"""

import os
import logging
from typing import Optional, List
from abc import ABC, abstractmethod
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Base class for AI providers"""

    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate text response from prompt"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass


class GroqProvider(AIProvider):
    """Groq API Provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from groq import Groq

            self.client = Groq(api_key=api_key)
            self.available = True
        except Exception as e:
            logger.warning(f"Groq provider initialization failed: {e}")
            self.available = False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response using Groq API"""
        if not self.available:
            raise Exception("Groq provider not available")

        try:
            message = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="mixtral-8x7b-32768",
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return message.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise

    def is_available(self) -> bool:
        return self.available


class GeminiProvider(AIProvider):
    """Google Gemini API Provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-pro")
            self.available = True
        except Exception as e:
            logger.warning(f"Gemini provider initialization failed: {e}")
            self.available = False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response using Gemini API"""
        if not self.available:
            raise Exception("Gemini provider not available")

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0.7,
                },
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    def is_available(self) -> bool:
        return self.available


class HuggingFaceProvider(AIProvider):
    """HuggingFace Inference API Provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_id = "mistralai/Mistral-7B-Instruct-v0.1"
        self.available = bool(api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response using HuggingFace Inference API"""
        if not self.available:
            raise Exception("HuggingFace provider not available")

        try:
            import httpx

            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": max_tokens},
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api-inference.huggingface.co/models/{self.model_id}",
                    headers=headers,
                    json=payload,
                    timeout=30,
                )
                result = response.json()
                if isinstance(result, list):
                    return result[0].get("generated_text", "")
                return result.get("generated_text", "")
        except Exception as e:
            logger.error(f"HuggingFace API error: {e}")
            raise

    def is_available(self) -> bool:
        return self.available


class OpenRouterProvider(AIProvider):
    """OpenRouter API Provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.available = bool(api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response using OpenRouter API"""
        if not self.available:
            raise Exception("OpenRouter provider not available")

        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/yourusername/job-agent",
                "X-Title": "AI Job Hunter",
            }

            payload = {
                "model": "mistralai/mistral-7b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30,
                )
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise

    def is_available(self) -> bool:
        return self.available


class OllamaProvider(AIProvider):
    """Local Ollama Provider"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "mistral"
        self.available = self._check_connection()

    def _check_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            import httpx

            response = httpx.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response using local Ollama"""
        if not self.available:
            raise Exception("Ollama provider not available")

        try:
            import httpx

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "num_predict": max_tokens,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=60,
                )
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise

    def is_available(self) -> bool:
        return self.available


class AIRouter:
    """Smart AI Router with Fallback System"""

    PRIORITY_ORDER = ["groq", "gemini", "huggingface", "openrouter", "ollama"]

    def __init__(self):
        self.providers = {}
        self._initialize_providers()
        self.current_provider = None

    def _initialize_providers(self):
        """Initialize all available AI providers"""
        # Groq
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            self.providers["groq"] = GroqProvider(groq_key)

        # Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            self.providers["gemini"] = GeminiProvider(gemini_key)

        # HuggingFace
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        if hf_key:
            self.providers["huggingface"] = HuggingFaceProvider(hf_key)

        # OpenRouter
        or_key = os.getenv("OPENROUTER_API_KEY")
        if or_key:
            self.providers["openrouter"] = OpenRouterProvider(or_key)

        # Ollama (always try to initialize)
        self.providers["ollama"] = OllamaProvider()

        logger.info(f"Initialized AI providers: {list(self.providers.keys())}")

    async def generate(
        self, prompt: str, provider: Optional[str] = None, max_tokens: int = 1024
    ) -> str:
        """Generate response with automatic fallback"""
        if not self.providers:
            raise Exception("No AI providers configured")

        # Use specified provider or try priority order
        providers_to_try = []

        if provider and provider in self.providers:
            providers_to_try = [provider]
        else:
            providers_to_try = [
                p for p in self.PRIORITY_ORDER if p in self.providers
            ]

        last_error = None
        for prov_name in providers_to_try:
            try:
                prov = self.providers[prov_name]
                if not prov.is_available():
                    continue

                logger.info(f"Using {prov_name} provider")
                self.current_provider = prov_name
                response = await prov.generate(prompt, max_tokens)
                return response

            except Exception as e:
                logger.warning(
                    f"{prov_name} failed, trying next provider: {str(e)}"
                )
                last_error = e
                continue

        raise Exception(
            f"All AI providers failed. Last error: {str(last_error)}"
        )

    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [
            name for name, prov in self.providers.items() if prov.is_available()
        ]

    def get_current_provider(self) -> Optional[str]:
        """Get currently active provider"""
        return self.current_provider


# Global AI Router instance
ai_router = None


def get_ai_router() -> AIRouter:
    """Get or create AI router instance"""
    global ai_router
    if ai_router is None:
        ai_router = AIRouter()
    return ai_router

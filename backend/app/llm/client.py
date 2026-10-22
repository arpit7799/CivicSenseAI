# =============================================================================
# CivicSense AI — LLM Client
# =============================================================================
# Asynchronous interface for local LLM communication via Ollama.
#
# Provides an abstract base class `LLMClient` to allow deterministic,
# zero-network unit testing using MockLLMClient.
#
# Owner: Arpit (Person 1)
# =============================================================================

from abc import ABC, abstractmethod
import asyncio
import json
from typing import Any
import httpx

from app.config import get_settings
from app.core.logging import get_logger
from app.core.errors import LLMGenerationError

logger = get_logger(__name__)


class LLMClient(ABC):
    """Abstract interface for LLM text generation."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate text from the LLM given a user prompt and optional system prompt."""
        ...


class OllamaClient(LLMClient):
    """
    Client for interacting with a locally running Ollama instance.
    Uses /api/generate with JSON format enforcement.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        temperature: float | None = None,
    ):
        settings = get_settings()
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout_seconds if timeout_seconds is not None else settings.ollama_timeout_seconds
        self.temperature = temperature if temperature is not None else settings.llm_temperature

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        url = f"{self.base_url}/api/generate"
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": self.temperature,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        logger.info(f"Dispatching generation request to Ollama ({self.model}) at {url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    raise LLMGenerationError(
                        f"Ollama returned HTTP {response.status_code}: {response.text[:200]}",
                        details={"status_code": response.status_code, "url": url},
                    )

                data = response.json()
                raw_response = data.get("response", "")
                if not raw_response:
                    raise LLMGenerationError("Ollama response contained empty output")
                return raw_response

        except httpx.TimeoutException as exc:
            logger.warning(f"Ollama request timed out after {self.timeout}s: {exc}")
            raise LLMGenerationError(
                f"Ollama generation timed out after {self.timeout}s",
                details={"timeout": self.timeout},
            ) from exc
        except httpx.RequestError as exc:
            logger.warning(f"Failed to connect to Ollama at {url}: {exc}")
            raise LLMGenerationError(
                f"Ollama connection error: {exc}",
                details={"url": url},
            ) from exc
        except Exception as exc:
            if isinstance(exc, LLMGenerationError):
                raise
            logger.error(f"Unexpected error during Ollama generation: {exc}")
            raise LLMGenerationError(f"Ollama generation failed: {exc}") from exc


class MockLLMClient(LLMClient):
    """
    Deterministic mock client for isolated unit testing.
    Does NOT require a running Ollama server or network access.
    """

    def __init__(
        self,
        default_response: str | None = None,
        should_fail: bool = False,
        failure_error: Exception | None = None,
        delay_seconds: float = 0.0,
    ):
        self.default_response = default_response
        self.should_fail = should_fail
        self.failure_error = failure_error
        self.delay_seconds = delay_seconds
        self.call_count = 0
        self.last_prompt = ""
        self.last_system_prompt = ""

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        self.call_count += 1
        self.last_prompt = prompt
        self.last_system_prompt = system_prompt or ""

        if self.delay_seconds > 0:
            await asyncio.sleep(self.delay_seconds)

        if self.should_fail:
            if self.failure_error:
                raise self.failure_error
            raise LLMGenerationError("Mock LLM connection error")

        if self.default_response is not None:
            return self.default_response

        # Default valid JSON response
        return json.dumps({
            "subject": "Urgent Civic Issue Report",
            "body": "A civic issue was identified and requires inspection and rectification.",
            "priority": "MEDIUM",
            "requested_action": "Inspect and repair the reported defect.",
        })

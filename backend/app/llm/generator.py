# =============================================================================
# CivicSense AI — Ollama Structured Complaint Generator
# =============================================================================
# Implements the ComplaintGenerator interface using local Ollama (Llama 3.2),
# structured prompt templates, application-side guardrails, and deterministic fallback.
#
# Owner: Arpit (Person 1)
# =============================================================================

from datetime import datetime, timezone
import json
import re
from typing import Any

from app.core.interfaces import ComplaintGenerator
from app.contracts.complaint import ComplaintResult
from app.core.logging import get_logger
from app.llm.client import LLMClient, OllamaClient
from app.llm.prompts import SYSTEM_PROMPT, build_complaint_prompt
from app.llm.guardrails import validate_and_sanitize_complaint
from app.llm.fallback import generate_deterministic_complaint

logger = get_logger(__name__)


class OllamaComplaintGenerator(ComplaintGenerator):
    """
    Structured complaint generator powered by Ollama (Llama 3.2).
    Includes application-side anti-hallucination guardrails and independent fallback.
    """

    def __init__(self, llm_client: LLMClient | None = None):
        self._client = llm_client or OllamaClient()

    async def generate(self, decision_context: dict[str, Any]) -> ComplaintResult:
        logger.info("Generating formal civic complaint using Ollama LLM")

        try:
            prompt = build_complaint_prompt(decision_context)
            raw_text = await self._client.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)

            # Clean markdown JSON block formatting if present
            cleaned = self._clean_json_output(raw_text)
            parsed_data = json.loads(cleaned)

            if not isinstance(parsed_data, dict):
                raise ValueError("LLM did not return a JSON object")

            # Application-side anti-hallucination validation
            validated = validate_and_sanitize_complaint(parsed_data, decision_context)

            logger.info("Complaint successfully generated and verified by anti-hallucination guardrails")
            return ComplaintResult(
                subject=validated["subject"].strip(),
                body=validated["body"].strip(),
                priority=validated["priority"],
                requested_action=validated.get("requested_action", "").strip() or None,
                generated_at=datetime.now(timezone.utc).isoformat(),
                source="ollama_llama3",
            )

        except Exception as exc:
            logger.warning(
                f"LLM complaint generation failed or violated guardrails: {exc}. "
                "Executing independent deterministic fallback."
            )
            return generate_deterministic_complaint(decision_context)

    @staticmethod
    def _clean_json_output(text: str) -> str:
        """Strip thinking tags and markdown code fence blocks if returned by the model."""
        text = text.strip()
        # Remove <think>...</think> block if emitted by thinking models
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        # Remove ```json ... ``` or ``` ... ```
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
        return text.strip()

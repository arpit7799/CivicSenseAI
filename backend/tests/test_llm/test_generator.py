# =============================================================================
# CivicSense AI — Ollama Complaint Generator Tests
# =============================================================================

import json
import pytest

from app.llm.client import MockLLMClient
from app.llm.generator import OllamaComplaintGenerator
from app.core.errors import LLMGenerationError


@pytest.fixture
def sample_context():
    return {
        "issue_type": "pothole",
        "severity_level": "HIGH",
        "address": "123 Main Street",
        "city": "Gurugram",
        "authority_name": "Municipal Corporation of Gurugram",
        "department": "Engineering Division",
        "contact_email": "mcg@gurugram.gov.in",
        "contact_phone": "01242370700",
        "rag_documents": ["Road repair procedure guideline"],
        "user_description": "Dangerous pothole near metro station.",
    }


@pytest.mark.anyio
async def test_generator_successful_with_clean_json(sample_context):
    mock_payload = {
        "subject": "HIGH Priority: Urgent Pothole Repair on Main Street",
        "body": "Dear MCG,\n\nA hazardous pothole has developed on Main Street near metro station.",
        "priority": "HIGH",
        "requested_action": "Fill and resurface the pothole.",
    }
    mock_client = MockLLMClient(default_response=json.dumps(mock_payload))
    generator = OllamaComplaintGenerator(llm_client=mock_client)

    result = await generator.generate(sample_context)

    assert result.source == "ollama_llama3"
    assert result.priority == "HIGH"
    assert result.subject == mock_payload["subject"]
    assert result.body == mock_payload["body"]
    assert result.requested_action == mock_payload["requested_action"]
    assert mock_client.call_count == 1


@pytest.mark.anyio
async def test_generator_handles_markdown_code_fence(sample_context):
    mock_payload = {
        "subject": "HIGH Priority: Pothole Report",
        "body": "Pothole needs repair on Main Street.",
        "priority": "HIGH",
        "requested_action": "Inspect defect.",
    }
    raw_markdown = f"```json\n{json.dumps(mock_payload)}\n```"
    mock_client = MockLLMClient(default_response=raw_markdown)
    generator = OllamaComplaintGenerator(llm_client=mock_client)

    result = await generator.generate(sample_context)

    assert result.source == "ollama_llama3"
    assert result.subject == mock_payload["subject"]


@pytest.mark.anyio
async def test_generator_triggers_fallback_on_llm_failure(sample_context):
    mock_client = MockLLMClient(
        should_fail=True,
        failure_error=LLMGenerationError("Ollama daemon unavailable on localhost:11434"),
    )
    generator = OllamaComplaintGenerator(llm_client=mock_client)

    result = await generator.generate(sample_context)

    # Must seamlessly trigger independent deterministic fallback rather than crashing
    assert result.source == "deterministic_fallback_v1"
    assert result.priority == "HIGH"
    assert "Pothole" in result.subject
    assert "123 Main Street" in result.body


@pytest.mark.anyio
async def test_generator_triggers_fallback_on_malformed_json(sample_context):
    mock_client = MockLLMClient(default_response="I am sorry, as an AI language model...")
    generator = OllamaComplaintGenerator(llm_client=mock_client)

    result = await generator.generate(sample_context)

    assert result.source == "deterministic_fallback_v1"
    assert result.priority == "HIGH"
    assert "Pothole" in result.subject


@pytest.mark.anyio
async def test_generator_triggers_fallback_on_hallucinated_contacts(sample_context):
    # LLM fabricates an unverified email
    mock_payload = {
        "subject": "HIGH Priority: Pothole Report",
        "body": "Please contact inspector.fake@potholerepair.org immediately.",
        "priority": "HIGH",
        "requested_action": "Inspect defect.",
    }
    mock_client = MockLLMClient(default_response=json.dumps(mock_payload))
    generator = OllamaComplaintGenerator(llm_client=mock_client)

    result = await generator.generate(sample_context)

    # Hallucination caught by application-side guardrails -> fallback invoked!
    assert result.source == "deterministic_fallback_v1"
    assert result.priority == "HIGH"
    assert "inspector.fake@potholerepair.org" not in result.body

# =============================================================================
# CivicSense AI — LLM Prompt Tests
# =============================================================================

import pytest
from app.llm.prompts import build_complaint_prompt, SYSTEM_PROMPT


def test_system_prompt_contains_anti_hallucination_rules():
    assert "ANTI-HALLUCINATION CONSTRAINTS" in SYSTEM_PROMPT
    assert "contact details" in SYSTEM_PROMPT.lower()
    assert "statutory deadlines" in SYSTEM_PROMPT.lower()
    assert "priority" in SYSTEM_PROMPT.lower()


def test_build_complaint_prompt_with_full_context():
    context = {
        "issue_type": "pothole",
        "severity_level": "HIGH",
        "address": "45 MG Road",
        "city": "Bengaluru",
        "authority_name": "BBMP",
        "department": "Road Infrastructure Division",
        "contact_email": "commissioner@bbmp.gov.in",
        "contact_phone": "08022660000",
        "office_address": "Hudson Circle, Bengaluru",
        "rag_documents": [
            "[VERIFIED_OFFICIAL] BBMP SOP: Potholes on arterial roads must be filled within 48 hours."
        ],
        "user_description": "Deep trench in middle of lane.",
    }

    prompt = build_complaint_prompt(context)
    assert "Pothole" in prompt
    assert "HIGH" in prompt
    assert "45 MG Road" in prompt
    assert "Bengaluru" in prompt
    assert "BBMP" in prompt
    assert "commissioner@bbmp.gov.in" in prompt
    assert "08022660000" in prompt
    assert "Deep trench in middle of lane." in prompt
    assert "Potholes on arterial roads must be filled" in prompt


def test_build_complaint_prompt_with_minimal_context():
    context = {
        "issue_type": "garbage_dump",
        "severity_level": "MEDIUM",
    }
    prompt = build_complaint_prompt(context)
    assert "Garbage Dump" in prompt
    assert "MEDIUM" in prompt
    assert "None provided (DO NOT INVENT ANY CONTACTS)" in prompt
    assert "No specific municipal charter documents available" in prompt

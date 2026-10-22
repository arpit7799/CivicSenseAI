# =============================================================================
# CivicSense AI — Anti-Hallucination Guardrail Tests
# =============================================================================

import pytest
from app.llm.guardrails import validate_and_sanitize_complaint, GuardrailViolationError


def test_guardrail_accepts_valid_complaint_and_aligns_priority():
    context = {
        "issue_type": "pothole",
        "severity_level": "CRITICAL",
        "contact_email": "complaints@civic.gov",
        "contact_phone": "9876543210",
        "rag_documents": [],
    }
    raw_data = {
        "subject": "CRITICAL: Urgent Pothole on Main Road",
        "body": "A deep pothole is causing vehicle damage. Contact: complaints@civic.gov",
        "priority": "LOW",  # LLM drifted
        "requested_action": "Repair immediately.",
    }

    validated = validate_and_sanitize_complaint(raw_data, context)
    # Priority is strictly synchronized to assessed severity level
    assert validated["priority"] == "CRITICAL"
    assert validated["subject"] == raw_data["subject"]


def test_guardrail_rejects_hallucinated_email():
    context = {
        "severity_level": "HIGH",
        "contact_email": None,  # No verified email
        "rag_documents": [],
    }
    raw_data = {
        "subject": "High Priority Streetlight Issue",
        "body": "Please email commissioner.fake@delhi.gov.in to report this defect.",
        "priority": "HIGH",
        "requested_action": "Fix wiring",
    }

    with pytest.raises(GuardrailViolationError, match="unverified email address"):
        validate_and_sanitize_complaint(raw_data, context)


def test_guardrail_rejects_hallucinated_phone():
    context = {
        "severity_level": "MEDIUM",
        "contact_phone": None,  # No verified phone
        "rag_documents": [],
    }
    raw_data = {
        "subject": "Garbage dump issue",
        "body": "Citizens should contact the helpline at +91 9876543210 for pickup.",
        "priority": "MEDIUM",
        "requested_action": "Clear waste",
    }

    with pytest.raises(GuardrailViolationError, match="unverified phone number"):
        validate_and_sanitize_complaint(raw_data, context)


def test_guardrail_rejects_unsupported_statutory_claim():
    context = {
        "severity_level": "HIGH",
        "rag_documents": ["Routine guidelines for municipal cleaning."],
    }
    raw_data = {
        "subject": "Water logging complaint",
        "body": "Under Section 42 of the Municipal Corporation Act, action must be taken within 24 hours.",
        "priority": "HIGH",
        "requested_action": "Clear drain",
    }

    with pytest.raises(GuardrailViolationError, match="unsupported statutory/procedural deadline"):
        validate_and_sanitize_complaint(raw_data, context)


def test_guardrail_allows_grounded_statutory_claim():
    context = {
        "severity_level": "HIGH",
        "rag_documents": [
            "Official SOP: Under Section 42 of the Municipal Corporation Act, clear within 24 hours."
        ],
    }
    raw_data = {
        "subject": "Water logging complaint",
        "body": "Under Section 42 of the Municipal Corporation Act, please clear the drain.",
        "priority": "HIGH",
        "requested_action": "Clear drain",
    }

    validated = validate_and_sanitize_complaint(raw_data, context)
    assert validated["priority"] == "HIGH"

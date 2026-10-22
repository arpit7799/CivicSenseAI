# =============================================================================
# CivicSense AI — Deterministic Complaint Fallback Tests
# =============================================================================

import pytest
from app.llm.fallback import generate_deterministic_complaint


def test_fallback_generates_valid_complaint_with_full_context():
    context = {
        "issue_type": "fallen_tree",
        "severity_level": "HIGH",
        "address": "12 Civil Lines",
        "city": "Nagpur",
        "authority_name": "Nagpur Municipal Corporation",
        "department": "Horticulture & Disaster Management",
        "contact_email": "tree.helpline@nmc.gov",
        "contact_phone": "07122567890",
        "user_description": "Large branch fell across electric poles.",
        "rag_documents": [],  # RAG is empty
    }

    result = generate_deterministic_complaint(context)

    assert result.priority == "HIGH"
    assert result.source == "deterministic_fallback_v1"
    assert "Fallen Tree" in result.subject
    assert "Nagpur" in result.subject
    assert "12 Civil Lines" in result.body
    assert "Large branch fell across electric poles." in result.body
    assert "tree.helpline@nmc.gov" in result.body
    assert "07122567890" in result.body
    assert result.requested_action is not None


def test_fallback_works_with_minimal_context_and_no_contacts():
    context = {
        "issue_type": "water_logging",
        "severity_level": "CRITICAL",
        "rag_documents": None,  # RAG is None
    }

    result = generate_deterministic_complaint(context)

    assert result.priority == "CRITICAL"
    assert result.source == "deterministic_fallback_v1"
    assert "Water Logging" in result.subject
    assert "CRITICAL" in result.subject
    assert "Verified Department Contact Records" not in result.body
    assert "@" not in result.body  # No fabricated emails


@pytest.mark.parametrize("level", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
def test_fallback_preserves_all_severity_levels(level):
    context = {
        "issue_type": "broken_streetlight",
        "severity_level": level,
    }
    result = generate_deterministic_complaint(context)
    assert result.priority == level

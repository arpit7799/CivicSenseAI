# =============================================================================
# CivicSense AI — Document Ingestion & Chunking Tests
# =============================================================================
# Tests paragraph preservation, text normalization, chunk size constraints,
# and verified source provenance tracking.
# =============================================================================

import pytest

from app.rag.ingestion import (
    CivicDocument,
    DocumentSource,
    VerificationStatus,
    clean_text,
    chunk_document,
)


def test_clean_text_normalizes_whitespace():
    raw = "  Pothole repair   \r\n\r\n  mandated by  the \t municipal code.  \n\n\n\nSection 2. "
    cleaned = clean_text(raw)
    assert "\r" not in cleaned
    assert "  " not in cleaned
    assert "Pothole repair\n\nmandated by the municipal code.\n\nSection 2." == cleaned


def test_chunking_preserves_verified_official_source():
    doc = CivicDocument(
        id="DOC-OFFICIAL-01",
        category="roads",
        source=DocumentSource(
            authority_name="Municipal Works Division",
            title="Road Restoration SOP",
            reference_id="ENG/2024/01",
            url="https://civic.gov/roads",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            department="Engineering",
            jurisdiction="Zone 1",
        ),
        text=(
            "Paragraph One: Official pothole repair rules.\n\n"
            "Paragraph Two: Emergency clearing within municipal limits."
        ),
    )

    chunks = chunk_document(doc, chunk_size=50, chunk_overlap=10)
    assert len(chunks) >= 1

    first = chunks[0]
    assert first.document_id == "DOC-OFFICIAL-01"
    assert first.source_authority == "Municipal Works Division"
    assert first.source_title == "Road Restoration SOP"
    assert first.verification_status == "verified_official"
    assert first.department == "Engineering"
    assert first.jurisdiction == "Zone 1"
    assert first.metadata["reference_id"] == "ENG/2024/01"


def test_chunking_preserves_verification_date():
    doc = CivicDocument(
        id="DOC-DATED-01",
        category="general",
        source=DocumentSource(
            authority_name="Official Civic Source",
            title="Published Contact Information",
            url="https://example.gov/contact",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            verified_at="2026-10-22",
        ),
        text="The official contact channel is listed here.",
    )

    chunk = chunk_document(doc)[0]
    assert chunk.metadata["verified_at"] == "2026-10-22"


def test_chunking_preserves_general_guidance_status():
    doc = CivicDocument(
        id="DOC-GUIDE-02",
        category="general",
        source=DocumentSource(
            authority_name="Civic Forum",
            title="Citizen Awareness Advice",
            verification_status=VerificationStatus.GENERAL_GUIDANCE,
        ),
        text="General advice for citizens reporting localized issues.",
    )

    chunks = chunk_document(doc)
    assert len(chunks) == 1
    assert chunks[0].verification_status == "general_guidance"
    assert chunks[0].source_authority == "Civic Forum"


def test_chunking_splits_large_text_with_overlap():
    long_para = "word " * 600
    doc = CivicDocument(
        id="DOC-LARGE-03",
        category="sanitation",
        source=DocumentSource(
            authority_name="Sanitation Dept",
            title="Waste Management Code",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
        ),
        text=long_para,
    )

    chunks = chunk_document(doc, chunk_size=200, chunk_overlap=40)
    assert len(chunks) >= 3
    for chunk in chunks:
        assert len(chunk.text.split()) <= 200
        assert chunk.verification_status == "verified_official"

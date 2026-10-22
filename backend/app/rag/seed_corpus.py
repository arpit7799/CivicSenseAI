# =============================================================================
# CivicSense AI — Verified Seed Civic Corpus
# =============================================================================
# Person 2 supplies sourced jurisdiction and civic-service records here;
# Arpit owns the RAG ingestion and retrieval implementation.
# =============================================================================

from app.rag.ingestion import CivicDocument, DocumentSource, VerificationStatus


SEED_CIVIC_DOCUMENTS: list[CivicDocument] = [
    CivicDocument(
        id="MCG-GURUGRAM-CIVIC-GRIEVANCE-01",
        category="general_civic_services",
        source=DocumentSource(
            authority_name="Municipal Corporation of Gurugram",
            title="Official civic grievance and contact information",
            reference_id="https://www.mcg.gov.in/",
            url="https://www.mcg.gov.in/",
            verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            jurisdiction="Municipal Corporation of Gurugram",
            verified_at="2026-10-22",
        ),
        text=(
            "The official Municipal Corporation of Gurugram website provides a "
            "Report Civic Issue and Track Status service. It lists the MCG "
            "toll-free number 18001801817 and the head office at Sector 34, "
            "Gurugram, Haryana 122001. This source supports a general MCG civic "
            "grievance route. It does not establish which department handles "
            "each individual issue category or promise a repair time."
        ),
    ),
    CivicDocument(
        id="CIVICSENSE-REPORTING-CHECKLIST-01",
        category="general_reporting_guidance",
        source=DocumentSource(
            authority_name="CivicSense AI",
            title="Information that helps describe a civic issue",
            reference_id="CivicSense product guidance",
            verification_status=VerificationStatus.GENERAL_GUIDANCE,
            jurisdiction="General guidance; not municipal policy",
        ),
        text=(
            "For a useful report, provide a clear photo, the issue location, a "
            "nearby landmark, and a short description of what is affected. This "
            "is CivicSense product guidance, not an official government rule."
        ),
    ),
]

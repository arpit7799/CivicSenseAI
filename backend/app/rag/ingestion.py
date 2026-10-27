# =============================================================================
# CivicSense AI — Document Ingestion & Chunking
# =============================================================================
# Processes raw municipal documents into structured, metadata-annotated
# text chunks ready for vector indexing.
#
# CRITICAL SOURCE RELIABILITY:
# Distinguishes verified official municipal guidelines from general guidance
# and unverified information. Preserves provenance attributes.
# =============================================================================

from dataclasses import dataclass, field
from enum import Enum
import re
import uuid


class VerificationStatus(str, Enum):
    """Reliability status of civic documentation."""
    VERIFIED_OFFICIAL = "verified_official"    # Official gazette/charter/SOP with verified authority source
    GENERAL_GUIDANCE = "general_guidance"      # Educational civic background info (not binding policy)
    UNVERIFIED = "unverified"                  # Community or uncorroborated submissions


@dataclass
class DocumentSource:
    """Provenance and authority metadata for a civic document."""
    authority_name: str
    title: str
    reference_id: str | None = None
    url: str | None = None
    verification_status: VerificationStatus = VerificationStatus.GENERAL_GUIDANCE
    department: str | None = None
    jurisdiction: str | None = None
    verified_at: str | None = None


@dataclass
class CivicDocument:
    """Raw civic document with source attribution."""
    id: str
    text: str
    source: DocumentSource
    category: str  # e.g., 'roads', 'sanitation', 'electricity', 'drainage'


@dataclass
class DocumentChunk:
    """Processed text chunk ready for vector embedding and retrieval."""
    chunk_id: str
    document_id: str
    text: str
    category: str
    source_authority: str
    source_title: str
    verification_status: str
    department: str | None = None
    jurisdiction: str | None = None
    metadata: dict = field(default_factory=dict)


def clean_text(text: str) -> str:
    """Normalize whitespace and strip unnecessary formatting artifacts."""
    text = re.sub(r"\r\n|\r", "\n", text)
    # Strip spaces per line and normalize intra-line whitespace
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def chunk_document(
    document: CivicDocument,
    chunk_size: int = 400,
    chunk_overlap: int = 50,
) -> list[DocumentChunk]:
    """
    Split a civic document into overlapping chunks while preserving
    paragraph integrity and full source attribution.
    """
    cleaned = clean_text(document.text)
    if not cleaned:
        return []

    # First, split by natural paragraph breaks
    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    chunks: list[DocumentChunk] = []

    current_chunk: list[str] = []
    current_length = 0

    for para in paragraphs:
        para_words = para.split(" ")
        para_len = len(para_words)

        # If a single paragraph is larger than chunk_size, split by words
        if para_len > chunk_size:
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append(
                    _create_chunk(document, chunk_text, len(chunks))
                )
                current_chunk = []
                current_length = 0

            start = 0
            while start < para_len:
                end = min(start + chunk_size, para_len)
                sub_text = " ".join(para_words[start:end])
                chunks.append(
                    _create_chunk(document, sub_text, len(chunks))
                )
                if end == para_len:
                    break
                start = end - chunk_overlap
            continue

        # If adding this paragraph exceeds chunk size, commit current chunk
        if current_length + para_len > chunk_size and current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(
                _create_chunk(document, chunk_text, len(chunks))
            )
            # Retain overlap words from end of current chunk
            overlap_words = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else []
            current_chunk = list(overlap_words)
            current_length = len(current_chunk)

        current_chunk.extend(para_words)
        current_length += para_len

    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunks.append(
            _create_chunk(document, chunk_text, len(chunks))
        )

    return chunks


def _create_chunk(doc: CivicDocument, text: str, index: int) -> DocumentChunk:
    chunk_id = f"{doc.id}_chunk_{index}_{str(uuid.uuid4())[:8]}"
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id=doc.id,
        text=text,
        category=doc.category,
        source_authority=doc.source.authority_name,
        source_title=doc.source.title,
        verification_status=doc.source.verification_status.value,
        department=doc.source.department,
        jurisdiction=doc.source.jurisdiction,
        metadata={
            "reference_id": doc.source.reference_id,
            "url": doc.source.url,
            "verified_at": doc.source.verified_at,
            "chunk_index": index,
        },
    )

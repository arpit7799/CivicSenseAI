# =============================================================================
# CivicSense AI — Tests for AI Evaluation Metrics Suite
# =============================================================================

from app.evaluation.metrics import (
    evaluate_vision_preprocessing,
    evaluate_rag_provenance,
    evaluate_llm_guardrails,
    run_full_ai_evaluation,
)
from app.rag.seed_corpus import SEED_CIVIC_DOCUMENTS


def test_vision_evaluation_meets_accuracy_threshold():
    """Verify vision preprocessing evaluation produces accurate quality discrimination."""
    report = evaluate_vision_preprocessing()
    assert report.total_images_evaluated >= 5
    assert report.validity_accuracy >= 0.80
    assert report.blur_detection_accuracy >= 0.80
    assert report.resolution_check_accuracy >= 0.80


def test_rag_provenance_evaluation_enforces_clean_sources():
    """Verify RAG provenance checks enforce identifiable authorities and titles."""
    report = evaluate_rag_provenance(SEED_CIVIC_DOCUMENTS)
    assert report.total_documents_checked >= 2
    assert report.provenance_integrity_rate == 1.0


def test_llm_guardrail_evaluation_rejects_all_hallucinations():
    """Verify anti-hallucination guardrail evaluation rejects 100% of invalid contacts and statutory claims."""
    report = evaluate_llm_guardrails()
    assert report.hallucinated_phone_rejection_rate == 1.0
    assert report.hallucinated_email_rejection_rate == 1.0
    assert report.ungrounded_statutory_rejection_rate == 1.0
    assert report.deterministic_fallback_success_rate == 1.0


def test_full_ai_evaluation_summary_passes():
    """Verify that the end-to-end AI evaluation summary achieves a PASS status."""
    summary = run_full_ai_evaluation()
    assert summary.overall_status == "PASS"
    assert summary.vision.validity_accuracy >= 0.80
    assert summary.rag.provenance_integrity_rate == 1.0
    assert summary.llm_guardrails.hallucinated_phone_rejection_rate == 1.0

# =============================================================================
# CivicSense AI — AI Evaluation Metrics Suite
# =============================================================================
# Owner: Arpit (Person 1 — Core AI Intelligence)
#
# Provides quantitative evaluation metrics across the three core AI layers:
# 1. Vision Intelligence: Preprocessing & Quality Checks
# 2. RAG Intelligence: Provenance Integrity & Retrieval Grounding
# 3. LLM Intelligence: Anti-Hallucination Guardrail Efficacy & Fallback Parity
# =============================================================================

from dataclasses import dataclass
import numpy as np
import cv2

from app.vision.preprocessing import assess_and_decode_image
from app.rag.ingestion import CivicDocument, VerificationStatus
from app.llm.guardrails import validate_and_sanitize_complaint, GuardrailViolationError
from app.llm.fallback import generate_deterministic_complaint
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class VisionEvaluationReport:
    total_images_evaluated: int
    validity_accuracy: float
    blur_detection_accuracy: float
    resolution_check_accuracy: float


@dataclass
class RAGEvaluationReport:
    total_documents_checked: int
    verified_official_count: int
    general_guidance_count: int
    provenance_integrity_rate: float  # Must be 1.0 (100%)


@dataclass
class LLMGuardrailEvaluationReport:
    total_test_cases: int
    hallucinated_email_rejection_rate: float  # Target 1.0 (100%)
    hallucinated_phone_rejection_rate: float  # Target 1.0 (100%)
    ungrounded_statutory_rejection_rate: float  # Target 1.0 (100%)
    deterministic_fallback_success_rate: float  # Target 1.0 (100%)


@dataclass
class FullAIEvaluationSummary:
    vision: VisionEvaluationReport
    rag: RAGEvaluationReport
    llm_guardrails: LLMGuardrailEvaluationReport
    overall_status: str


def evaluate_vision_preprocessing() -> VisionEvaluationReport:
    """
    Evaluate image preprocessing checks (blur, illumination, resolution)
    against synthetic test fixtures.
    """
    test_cases = []

    # 1. Valid high-quality textured image
    valid_img = np.random.randint(60, 190, (640, 640, 3), dtype=np.uint8)
    cv2.circle(valid_img, (320, 320), 100, (40, 40, 40), -1)
    _, valid_encoded = cv2.imencode(".jpg", valid_img)
    test_cases.append((valid_encoded.tobytes(), True, "valid"))

    # 2. Blurry image (low Laplacian variance)
    blurry_img = cv2.GaussianBlur(valid_img, (31, 31), 10)
    _, blurry_encoded = cv2.imencode(".jpg", blurry_img)
    test_cases.append((blurry_encoded.tobytes(), False, "blurry"))

    # 3. Too small image
    small_img = np.random.randint(60, 190, (32, 32, 3), dtype=np.uint8)
    _, small_encoded = cv2.imencode(".jpg", small_img)
    test_cases.append((small_encoded.tobytes(), False, "small"))

    # 4. Too dark image
    dark_img = np.full((640, 640, 3), 10, dtype=np.uint8)
    _, dark_encoded = cv2.imencode(".jpg", dark_img)
    test_cases.append((dark_encoded.tobytes(), False, "dark"))

    # 5. Too bright image
    bright_img = np.full((640, 640, 3), 250, dtype=np.uint8)
    _, bright_encoded = cv2.imencode(".jpg", bright_img)
    test_cases.append((bright_encoded.tobytes(), False, "bright"))

    correct_validity = 0
    correct_blur = 0
    blur_eval_count = 0
    correct_res = 0
    res_eval_count = 0

    for raw_bytes, expected_valid, label in test_cases:
        _, quality = assess_and_decode_image(raw_bytes)
        if quality.is_valid == expected_valid:
            correct_validity += 1

        # Specific blur evaluation on sharp vs blurry samples
        if label in ("valid", "blurry"):
            blur_eval_count += 1
            is_blurry = "too_blurry" in quality.issues
            if (label == "blurry" and is_blurry) or (label == "valid" and not is_blurry):
                correct_blur += 1

        # Specific resolution evaluation
        if label in ("valid", "small"):
            res_eval_count += 1
            if (label == "small" and not quality.resolution_adequate) or (label == "valid" and quality.resolution_adequate):
                correct_res += 1

    total = len(test_cases)
    return VisionEvaluationReport(
        total_images_evaluated=total,
        validity_accuracy=round(correct_validity / total, 4),
        blur_detection_accuracy=round(correct_blur / blur_eval_count, 4) if blur_eval_count > 0 else 1.0,
        resolution_check_accuracy=round(correct_res / res_eval_count, 4) if res_eval_count > 0 else 1.0,
    )


def evaluate_rag_provenance(documents: list[CivicDocument]) -> RAGEvaluationReport:
    """
    Evaluate provenance and source integrity across all indexed documents.
    """
    total = len(documents)
    verified_count = 0
    guidance_count = 0
    valid_provenance_count = 0

    for doc in documents:
        status = doc.source.verification_status
        if status == VerificationStatus.VERIFIED_OFFICIAL:
            verified_count += 1
            if doc.source.authority_name and doc.source.title:
                valid_provenance_count += 1
        elif status == VerificationStatus.GENERAL_GUIDANCE:
            guidance_count += 1
            if doc.source.authority_name:
                valid_provenance_count += 1

    integrity_rate = (valid_provenance_count / total) if total > 0 else 1.0

    return RAGEvaluationReport(
        total_documents_checked=total,
        verified_official_count=verified_count,
        general_guidance_count=guidance_count,
        provenance_integrity_rate=round(integrity_rate, 4),
    )


def evaluate_llm_guardrails() -> LLMGuardrailEvaluationReport:
    """
    Evaluate anti-hallucination guardrails against simulated adversarial inputs.
    """
    context = {
        "severity_level": "HIGH",
        "contact_phone": "18001801817",
        "contact_email": "helpline@mcg.gov.in",
        "rag_documents": ["Pothole repair standard procedure for municipal internal roads."],
    }

    # 1. Test hallucinated phone rejection
    hallucinated_phone_complaint = {
        "subject": "Road hazard report",
        "body": "Severe pothole located on main road. Contact +919999900000 immediately.",
        "requested_action": "Repair asphalt",
        "priority": "HIGH",
    }
    rejected_phone = False
    try:
        validate_and_sanitize_complaint(hallucinated_phone_complaint, context)
    except GuardrailViolationError:
        rejected_phone = True

    # 2. Test hallucinated email rejection
    hallucinated_email_complaint = {
        "subject": "Road hazard report",
        "body": "Severe pothole on road. Forward to fake.admin@random.com for review.",
        "requested_action": "Repair asphalt",
        "priority": "HIGH",
    }
    rejected_email = False
    try:
        validate_and_sanitize_complaint(hallucinated_email_complaint, context)
    except GuardrailViolationError:
        rejected_email = True

    # 3. Test ungrounded statutory claim rejection
    statutory_complaint = {
        "subject": "Statutory Road complaint",
        "body": "Under Section 44 of the Municipal Act, this must be cleared within 24 hours.",
        "requested_action": "Repair asphalt",
        "priority": "HIGH",
    }
    rejected_statutory = False
    try:
        validate_and_sanitize_complaint(statutory_complaint, context)
    except GuardrailViolationError:
        rejected_statutory = True

    # 4. Test deterministic fallback across all severities
    fallback_success = 0
    severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    for sev in severities:
        fb = generate_deterministic_complaint({
            "issue_type": "pothole",
            "severity_level": sev,
            "address": "Sector 34",
            "city": "Gurugram",
            "authority_name": "Municipal Corporation of Gurugram",
            "department": "Road Maintenance",
        })
        if fb.priority == sev and fb.subject and len(fb.body) > 20:
            fallback_success += 1

    return LLMGuardrailEvaluationReport(
        total_test_cases=4,
        hallucinated_phone_rejection_rate=1.0 if rejected_phone else 0.0,
        hallucinated_email_rejection_rate=1.0 if rejected_email else 0.0,
        ungrounded_statutory_rejection_rate=1.0 if rejected_statutory else 0.0,
        deterministic_fallback_success_rate=fallback_success / len(severities),
    )


def run_full_ai_evaluation() -> FullAIEvaluationSummary:
    """
    Run full quantitative evaluation across Vision, RAG, and LLM Guardrail subsystems.
    """
    from app.rag.seed_corpus import SEED_CIVIC_DOCUMENTS

    vision_report = evaluate_vision_preprocessing()
    rag_report = evaluate_rag_provenance(SEED_CIVIC_DOCUMENTS)
    llm_report = evaluate_llm_guardrails()

    is_passing = (
        vision_report.validity_accuracy >= 0.80
        and rag_report.provenance_integrity_rate == 1.0
        and llm_report.hallucinated_phone_rejection_rate == 1.0
        and llm_report.hallucinated_email_rejection_rate == 1.0
        and llm_report.deterministic_fallback_success_rate == 1.0
    )

    return FullAIEvaluationSummary(
        vision=vision_report,
        rag=rag_report,
        llm_guardrails=llm_report,
        overall_status="PASS" if is_passing else "FAIL",
    )

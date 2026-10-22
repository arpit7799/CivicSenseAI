# =============================================================================
# CivicSense AI — End-to-End Pipeline Integration Suite (Phase 9)
# =============================================================================
# Owner: Arpit (Person 1 — Core AI Intelligence)
#
# Validates the full lifecycle:
# Raw Image + GPS -> Vision Detection -> Issue Classification ->
# Severity Assessment -> Concurrent Location/RAG/Duplicate ->
# Authority Routing -> LLM Complaint Generation -> Anti-Hallucination Guardrails
# =============================================================================

from pathlib import Path
import pytest

from app.decision.engine import DecisionEngine
from app.contracts.analysis import AnalysisRequest, AnalysisResponse
from app.vision.detector import YOLODetector
from app.vision.mock_detector import MockVisionDetector
from app.severity.engine import SeverityEngine
from app.location.mock_provider import MockLocationProvider
from app.authority.mock_provider import MockAuthorityProvider
from app.authority.dataset_provider import VerifiedDatasetAuthorityProvider
from app.duplicate.mock_detector import MockDuplicateDetector
from app.rag.retriever import QdrantRAGRetriever
from app.rag.embeddings import MockEmbeddingModel
from app.rag.ingestion import CivicDocument, DocumentSource, VerificationStatus
from app.llm.client import MockLLMClient
from app.llm.generator import OllamaComplaintGenerator
from app.contracts.vision import VisionResult, ImageQuality
from app.contracts.location import LocationResult, Coordinates


@pytest.fixture
def test_image_path() -> str:
    path = Path(__file__).resolve().parents[1] / "datasets" / "civic_dataset" / "images" / "val" / "civic_val_0000.jpg"
    return str(path)


@pytest.fixture
def trained_yolo_path() -> str:
    path = Path(__file__).resolve().parents[1] / "models" / "civicsense_yolo.pt"
    return str(path)


@pytest.mark.asyncio
async def test_e2e_pipeline_full_live_happy_path(test_image_path, trained_yolo_path):
    """
    Test the full end-to-end pipeline with fine-tuned YOLO, real severity rules,
    verified authority dataset, in-memory Qdrant RAG, and LLM generator.
    """
    if not Path(trained_yolo_path).exists() or not Path(test_image_path).exists():
        pytest.skip("Trained YOLO model or test validation image not found.")

    # 1. Vision: Fine-tuned YOLOv8
    vision = YOLODetector(model_path=trained_yolo_path)

    # 2. Severity: Rules-based engine
    severity = SeverityEngine()

    # 3. Location: Resolves Gurugram
    class GurugramLocationProvider:
        async def resolve(self, lat: float, lon: float) -> LocationResult:
            return LocationResult(
                address="Sector 34, Gurugram, Haryana",
                city="Gurugram",
                state="Haryana",
                coordinates=Coordinates(latitude=lat, longitude=lon),
                confidence=0.95,
                source="nominatim",
            )

    # 4. Authority: Verified Gurugram dataset provider
    dataset_path = Path(__file__).resolve().parents[1] / "datasets" / "authority_routes.json"
    authority = VerifiedDatasetAuthorityProvider(dataset_path=dataset_path)

    # 5. Duplicate: Clean check
    duplicate = MockDuplicateDetector()

    # 6. RAG: In-memory Qdrant with deterministic mock embeddings
    mock_embed = MockEmbeddingModel(dimension=64)
    rag = QdrantRAGRetriever(embedding_model=mock_embed, in_memory=True)
    rag.index_documents([
        CivicDocument(
            id="MCG-ROAD-SOP",
            category="roads",
            source=DocumentSource(
                authority_name="Municipal Corporation of Gurugram",
                title="Road Hazard Protocol",
                verification_status=VerificationStatus.VERIFIED_OFFICIAL,
            ),
            text="Potholes on municipal roadways must be inspected and barricaded within standard protocol.",
        )
    ])

    # 7. LLM: Clean structured generator with verified contact grounding
    clean_llm_json = """{
        "subject": "Hazardous road pothole requiring prompt intervention",
        "body": "A deep road cavity has formed on the transit corridor, presenting an immediate safety hazard for commuters. Please dispatch road engineering crew.",
        "priority": "HIGH",
        "requested_action": "Patch road crater",
        "authority_name": "Municipal Corporation of Gurugram",
        "department": null,
        "contact_phone": "18001801817",
        "contact_email": null,
        "suggested_actions": ["Cordon off hazard", "Patch road crater"]
    }"""
    llm_client = MockLLMClient(default_response=clean_llm_json)
    complaint_gen = OllamaComplaintGenerator(llm_client=llm_client)

    # 8. Orchestrate with Decision Engine
    engine = DecisionEngine(
        vision=vision,
        severity=severity,
        location=GurugramLocationProvider(),
        authority=authority,
        rag=rag,
        complaint=complaint_gen,
        duplicate=duplicate,
    )

    request = AnalysisRequest(
        image_url=test_image_path,
        latitude=28.4595,
        longitude=77.0266,
        user_description="Large dangerous pothole causing vehicular damage",
    )

    response: AnalysisResponse = await engine.analyze(request)

    # Assertions
    assert response.status == "completed"
    assert response.issue.type == "pothole"
    assert response.issue.confidence >= 0.50
    assert response.severity.level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert response.location.city == "Gurugram"
    assert response.authority.authority_name == "Municipal Corporation of Gurugram"
    assert response.authority.contact_phone == "18001801817"
    assert response.complaint.priority == response.severity.level
    assert "pothole" in response.complaint.subject.lower() or "road" in response.complaint.subject.lower()
    assert len(response.complaint.body) > 30
    assert response.duplicate_check is not None
    assert response.duplicate_check.is_potential_duplicate is False


@pytest.mark.asyncio
async def test_e2e_pipeline_short_circuit_on_non_civic_image():
    """
    When an image contains no detected civic issues, the pipeline short-circuits
    with status='rejected_no_civic_issue' and skips downstream LLM & RAG.
    """
    class NonCivicVisionDetector:
        async def detect(self, image_path: str) -> VisionResult:
            return VisionResult(
                detections=[],
                primary_issue=None,
                secondary_issues=[],
                image_quality=ImageQuality(
                    is_valid=True,
                    resolution_adequate=True,
                    blur_score=0.1,
                    overall_quality_score=0.9,
                ),
                classification_status="no_civic_issue_detected",
                processing_time_ms=10.0,
                model_version="test_v1",
                source="mock",
            )

    from app.severity.mock_engine import MockSeverityEngine
    from app.rag.mock_retriever import MockRAGRetriever
    from app.llm.mock_generator import MockComplaintGenerator

    engine = DecisionEngine(
        vision=NonCivicVisionDetector(),
        severity=MockSeverityEngine(),
        location=MockLocationProvider(),
        authority=MockAuthorityProvider(),
        rag=MockRAGRetriever(),
        complaint=MockComplaintGenerator(),
        duplicate=MockDuplicateDetector(),
    )

    request = AnalysisRequest(
        image_url="https://example.com/clean_street.jpg",
        latitude=28.4595,
        longitude=77.0266,
    )

    response = await engine.analyze(request)

    assert response.status == "rejected_no_civic_issue"
    assert response.issue.type == "unknown"
    assert response.severity is None
    assert response.complaint is None
    assert response.authority is None


@pytest.mark.asyncio
async def test_e2e_pipeline_degraded_location_failure():
    """
    When location resolution fails, authority routing is honestly skipped (dependency enforcement)
    and status is recorded as 'partial' without fabricated contacts.
    """
    class FailingLocationProvider:
        async def resolve(self, lat: float, lon: float):
            raise ConnectionError("Geocoding service unavailable")

    from app.rag.mock_retriever import MockRAGRetriever
    from app.llm.mock_generator import MockComplaintGenerator

    engine = DecisionEngine(
        vision=MockVisionDetector(),
        severity=SeverityEngine(),
        location=FailingLocationProvider(),
        authority=MockAuthorityProvider(),
        rag=MockRAGRetriever(),
        complaint=MockComplaintGenerator(),
        duplicate=MockDuplicateDetector(),
    )

    request = AnalysisRequest(
        image_url="https://example.com/pothole.jpg",
        latitude=28.4595,
        longitude=77.0266,
    )

    response = await engine.analyze(request)

    assert response.status == "partial"
    assert response.metadata.providers.get("location") == "failed"
    assert response.authority is None


@pytest.mark.asyncio
async def test_e2e_pipeline_llm_hallucination_triggers_deterministic_fallback():
    """
    If the LLM generates a hallucinated contact phone not in the verified authority,
    the guardrail catches it and falls back to deterministic generation.
    """
    hallucinated_llm_json = """{
        "subject": "Road hazard report",
        "body": "Pothole on road. Call +919876543210 urgently.",
        "priority": "HIGH",
        "requested_action": "Fix road",
        "authority_name": "Municipal Corporation of Gurugram",
        "department": null,
        "contact_phone": "+919876543210",
        "contact_email": null,
        "suggested_actions": ["Fix road"]
    }"""
    llm_client = MockLLMClient(default_response=hallucinated_llm_json)
    complaint_gen = OllamaComplaintGenerator(llm_client=llm_client)

    dataset_path = Path(__file__).resolve().parents[1] / "datasets" / "authority_routes.json"
    authority = VerifiedDatasetAuthorityProvider(dataset_path=dataset_path)

    from app.rag.mock_retriever import MockRAGRetriever

    engine = DecisionEngine(
        vision=MockVisionDetector(),
        severity=SeverityEngine(),
        location=MockLocationProvider(),
        authority=authority,
        rag=MockRAGRetriever(),
        complaint=complaint_gen,
        duplicate=MockDuplicateDetector(),
    )

    request = AnalysisRequest(
        image_url="https://example.com/pothole.jpg",
        latitude=28.4595,
        longitude=77.0266,
    )

    response = await engine.analyze(request)

    assert response.status == "completed"
    # Deterministic fallback generated the complaint
    assert response.complaint.source == "deterministic_fallback_v1"
    # Contact phone is not in complaint body
    assert "+919876543210" not in response.complaint.body

# =============================================================================
# CivicSense AI — Decision Engine (Skeleton)
# =============================================================================
# Orchestrates all AI pipeline stages into a unified analysis result.
#
# In Phase 1, this simply wires mock providers together.
# Real orchestration logic will be implemented in Phase 5.
#
# ARCHITECTURE RULE: This engine depends ONLY on abstract interfaces
# (from app.core.interfaces), never on concrete implementations.
#
# Owner: Arpit (Person 1)
# =============================================================================

import uuid
import time

from app.core.interfaces import (
    VisionProvider,
    SeverityProvider,
    LocationProvider,
    AuthorityProvider,
    RAGProvider,
    ComplaintGenerator,
    DuplicateDetector,
)
from app.contracts.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisMetadata,
    IssueInfo,
)
from app.core.logging import get_logger
from app.core.errors import AIServiceError

logger = get_logger(__name__)


class DecisionEngine:
    """
    Core AI Decision Engine — orchestrates the full analysis pipeline.

    Combines outputs from:
    - VisionProvider (Arpit)
    - SeverityProvider (Arpit)
    - LocationProvider (Arnav)
    - AuthorityProvider (Arnav)
    - RAGProvider (Arpit)
    - ComplaintGenerator (Arpit)
    - DuplicateDetector (Arnav)

    All dependencies are injected via constructor — no direct imports
    of concrete implementations.
    """

    def __init__(
        self,
        vision: VisionProvider,
        severity: SeverityProvider,
        location: LocationProvider,
        authority: AuthorityProvider,
        rag: RAGProvider,
        complaint: ComplaintGenerator,
        duplicate: DuplicateDetector,
    ):
        self._vision = vision
        self._severity = severity
        self._location = location
        self._authority = authority
        self._rag = rag
        self._complaint = complaint
        self._duplicate = duplicate

    async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Run the full AI analysis pipeline.

        Phase 1: Calls all mock providers in sequence.
        Phase 5+: Will include real orchestration, validation,
                  error recovery, and partial-result handling.
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(f"[{request_id}] Starting analysis for image: {request.image_url}")

        try:
            # Step 1: Vision detection (Arpit)
            vision_result = await self._vision.detect(request.image_url)

            # --- Phase 3: Short-Circuit on No Civic Issue ---
            if vision_result.classification_status == "no_civic_issue_detected":
                logger.info(f"[{request_id}] No valid civic issue detected. Short-circuiting.")
                elapsed_ms = (time.time() - start_time) * 1000
                return AnalysisResponse(
                    request_id=request_id,
                    status="rejected_no_civic_issue",
                    issue=IssueInfo(type="unknown", confidence=0.0),
                    severity=None,
                    location=None,
                    authority=None,
                    complaint=None,
                    duplicate_check=None,
                    vision_details=vision_result,
                    metadata=AnalysisMetadata(
                        request_id=request_id,
                        processing_time_ms=elapsed_ms,
                        api_version="v1",
                        providers={"vision": vision_result.source}
                    )
                )

            # Step 2: Severity assessment (Arpit)
            severity_result = await self._severity.assess(vision_result)

            # Step 3: Location resolution (Arnav)
            location_result = await self._location.resolve(
                request.latitude, request.longitude
            )

            # Step 4: Authority routing (Arnav)
            primary_issue_type = (
                vision_result.primary_issue.issue_class
                if vision_result.primary_issue
                else "unknown"
            )
            authority_result = await self._authority.route(
                primary_issue_type, location_result
            )

            # Step 5: RAG retrieval (Arpit)
            rag_query = f"{primary_issue_type} {location_result.city}"
            if request.user_description:
                rag_query = f"{request.user_description} {rag_query}"
            rag_result = await self._rag.retrieve(rag_query)

            # Step 6: Complaint generation (Arpit)
            decision_context = {
                "issue_type": primary_issue_type,
                "severity_level": severity_result.level,
                "address": location_result.address,
                "city": location_result.city,
                "authority_name": authority_result.authority_name,
                "department": authority_result.department,
                "rag_documents": rag_result.get("documents", []),
                "user_description": request.user_description or "",
            }
            complaint_result = await self._complaint.generate(decision_context)

            # Step 7: Duplicate check (Arnav)
            duplicate_result = await self._duplicate.check(
                issue_type=primary_issue_type,
                latitude=request.latitude,
                longitude=request.longitude,
                description=request.user_description,
                image_url=request.image_url,
            )

            elapsed_ms = (time.time() - start_time) * 1000

            # Build response
            issue_info = IssueInfo(
                type=primary_issue_type,
                confidence=(
                    vision_result.primary_issue.confidence
                    if vision_result.primary_issue
                    else 0.0
                ),
            )

            metadata = AnalysisMetadata(
                request_id=request_id,
                processing_time_ms=elapsed_ms,
                api_version="v1",
                providers={
                    "vision": vision_result.source,
                    "severity": severity_result.source,
                    "location": location_result.source,
                    "authority": authority_result.source,
                    "rag": rag_result.get("source", "unknown"),
                    "complaint": complaint_result.source,
                    "duplicate": duplicate_result.source,
                },
            )

            response = AnalysisResponse(
                request_id=request_id,
                status="completed",
                issue=issue_info,
                severity=severity_result,
                location=location_result,
                authority=authority_result,
                complaint=complaint_result,
                duplicate_check=duplicate_result,
                vision_details=vision_result,
                metadata=metadata,
            )

            logger.info(
                f"[{request_id}] Analysis completed in {elapsed_ms:.1f}ms — "
                f"issue={primary_issue_type}, severity={severity_result.level}"
            )

            return response

        except Exception as e:
            logger.exception(f"[{request_id}] Analysis failed: {e}")
            raise AIServiceError(
                message=f"Analysis pipeline failed: {str(e)}",
                details={"request_id": request_id},
            )

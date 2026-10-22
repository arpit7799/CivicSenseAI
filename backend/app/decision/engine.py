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

import asyncio
import time
import uuid

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
from app.contracts.location import LocationResult
from app.contracts.authority import AuthorityResult
from app.contracts.duplicate import DuplicateResult
from app.contracts.complaint import ComplaintResult
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

        Execution Flow:
        1. Image Intelligence (Vision): validate image and detect civic issues.
           - Short-circuit immediately if no civic issue is detected.
        2. Severity Engine: calculate severity score and level.
        3. Concurrent Phase (independent tasks):
           - Location Resolution (LocationProvider)
           - RAG Retrieval (RAGProvider)
           - Duplicate Detection (DuplicateDetector)
        4. Dependent Phase:
           - Authority Routing (AuthorityProvider) — requires valid Location & Issue
        5. Context Assembly & Complaint Generation (ComplaintGenerator).
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        providers_status: dict[str, str] = {}
        provider_times_ms: dict[str, float] = {}
        has_partial_failure = False

        logger.info(f"[{request_id}] Starting analysis for image: {request.image_url}")

        try:
            # -------------------------------------------------------------
            # Stage 1: Vision Detection (Critical)
            # -------------------------------------------------------------
            t0 = time.time()
            vision_result = await self._vision.detect(request.image_url)
            provider_times_ms["vision"] = round((time.time() - t0) * 1000, 2)
            providers_status["vision"] = vision_result.source

            # Phase 3: Short-Circuit on No Civic Issue
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
                        providers=providers_status,
                    ),
                )

            primary_issue_type = (
                vision_result.primary_issue.issue_class
                if vision_result.primary_issue
                else "unknown"
            )

            # -------------------------------------------------------------
            # Stage 2: Severity Assessment (Critical)
            # -------------------------------------------------------------
            t0 = time.time()
            severity_result = await self._severity.assess(vision_result)
            provider_times_ms["severity"] = round((time.time() - t0) * 1000, 2)
            providers_status["severity"] = severity_result.source

            # -------------------------------------------------------------
            # Stage 3: Concurrent Execution (Location, RAG, Duplicate)
            # -------------------------------------------------------------
            # Define isolated helper tasks with explicit error handling so
            # failure in one does not cancel or corrupt unrelated providers.
            async def _run_location() -> LocationResult | None:
                t_sub = time.time()
                try:
                    res = await self._location.resolve(request.latitude, request.longitude)
                    provider_times_ms["location"] = round((time.time() - t_sub) * 1000, 2)
                    providers_status["location"] = res.source
                    return res
                except Exception as exc:
                    provider_times_ms["location"] = round((time.time() - t_sub) * 1000, 2)
                    providers_status["location"] = "failed"
                    logger.warning(f"[{request_id}] Location resolution failed: {exc}")
                    return None

            async def _run_rag() -> dict | None:
                t_sub = time.time()
                try:
                    query = f"{primary_issue_type}"
                    if request.user_description:
                        query = f"{request.user_description} {query}"
                    res = await self._rag.retrieve(query)
                    provider_times_ms["rag"] = round((time.time() - t_sub) * 1000, 2)
                    providers_status["rag"] = res.get("source", "unknown")
                    return res
                except Exception as exc:
                    provider_times_ms["rag"] = round((time.time() - t_sub) * 1000, 2)
                    providers_status["rag"] = "failed"
                    logger.warning(f"[{request_id}] RAG retrieval failed: {exc}")
                    return None

            async def _run_duplicate() -> DuplicateResult | None:
                t_sub = time.time()
                try:
                    res = await self._duplicate.check(
                        issue_type=primary_issue_type,
                        latitude=request.latitude,
                        longitude=request.longitude,
                        description=request.user_description,
                        image_url=request.image_url,
                    )
                    provider_times_ms["duplicate"] = round((time.time() - t_sub) * 1000, 2)
                    providers_status["duplicate"] = res.source
                    return res
                except Exception as exc:
                    provider_times_ms["duplicate"] = round((time.time() - t_sub) * 1000, 2)
                    providers_status["duplicate"] = "failed"
                    logger.warning(f"[{request_id}] Duplicate check failed: {exc}")
                    return None

            # Execute independent operations concurrently
            location_result, rag_result, duplicate_result = await asyncio.gather(
                _run_location(),
                _run_rag(),
                _run_duplicate(),
            )

            if location_result is None or rag_result is None or duplicate_result is None:
                has_partial_failure = True

            # -------------------------------------------------------------
            # Stage 4: Dependent Authority Routing
            # Requires resolved location information. If location resolution
            # failed or is unavailable, authority routing MUST be skipped.
            # -------------------------------------------------------------
            authority_result: AuthorityResult | None = None
            if location_result is not None:
                t0 = time.time()
                try:
                    authority_result = await self._authority.route(
                        primary_issue_type, location_result
                    )
                    provider_times_ms["authority"] = round((time.time() - t0) * 1000, 2)
                    providers_status["authority"] = authority_result.source
                except Exception as exc:
                    provider_times_ms["authority"] = round((time.time() - t0) * 1000, 2)
                    providers_status["authority"] = "failed"
                    has_partial_failure = True
                    logger.warning(f"[{request_id}] Authority routing failed: {exc}")
                    authority_result = None
            else:
                logger.info(
                    f"[{request_id}] Skipping authority routing because location resolution is unavailable"
                )
                providers_status["authority"] = "skipped_due_to_unresolved_location"
                has_partial_failure = True

            # -------------------------------------------------------------
            # Stage 5: Context Assembly & Complaint Generation
            # Assembles available outputs cleanly.
            # -------------------------------------------------------------
            address_str = location_result.address if location_result else "Unresolved Location"
            city_str = location_result.city if location_result else "Unresolved City"
            auth_name = (
                authority_result.authority_name
                if authority_result
                else "Unassigned Authority"
            )
            dept_name = (
                authority_result.department
                if authority_result
                else "General Civic Department"
            )
            rag_docs = rag_result.get("documents", []) if rag_result else []

            decision_context = {
                "issue_type": primary_issue_type,
                "severity_level": severity_result.level,
                "address": address_str,
                "city": city_str,
                "authority_name": auth_name,
                "department": dept_name,
                "contact_email": authority_result.contact_email if authority_result else None,
                "contact_phone": authority_result.contact_phone if authority_result else None,
                "office_address": authority_result.office_address if authority_result else None,
                "rag_documents": rag_docs,
                "user_description": request.user_description or "",
            }

            complaint_result: ComplaintResult | None = None
            t0 = time.time()
            try:
                complaint_result = await self._complaint.generate(decision_context)
                provider_times_ms["complaint"] = round((time.time() - t0) * 1000, 2)
                providers_status["complaint"] = complaint_result.source
            except Exception as exc:
                provider_times_ms["complaint"] = round((time.time() - t0) * 1000, 2)
                providers_status["complaint"] = "failed"
                has_partial_failure = True
                logger.warning(f"[{request_id}] Complaint generation failed: {exc}")

            elapsed_ms = (time.time() - start_time) * 1000

            overall_status = "partial" if has_partial_failure else "completed"

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
                providers=providers_status,
            )

            response = AnalysisResponse(
                request_id=request_id,
                status=overall_status,
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
                f"[{request_id}] Analysis finished in {elapsed_ms:.1f}ms (status={overall_status}) — "
                f"issue={primary_issue_type}, severity={severity_result.level}"
            )

            return response

        except Exception as e:
            logger.exception(f"[{request_id}] Analysis pipeline failed: {e}")
            raise AIServiceError(
                message=f"Analysis pipeline failed: {str(e)}",
                details={"request_id": request_id},
            )


# =============================================================================
# CivicSense AI — Issue Classifier
# =============================================================================
# Owner: Arpit (Person 1)
# =============================================================================

from app.config import get_settings
from app.contracts.vision import Detection
from app.core.logging import get_logger

logger = get_logger(__name__)

def classify_detections(detections: list[Detection]) -> tuple[Detection | None, list[Detection], str]:
    """
    Filter raw YOLO detections based on confidence thresholds and the civic ontology.
    
    Returns:
        tuple containing:
        - primary_issue: Detection or None
        - secondary_issues: list[Detection]
        - classification_status: str
    """
    settings = get_settings()
    
    # 1. Filter by confidence and civic ontology
    valid_civic_issues = []
    
    for det in detections:
        # Check confidence
        if det.confidence < settings.min_confidence_threshold:
            logger.debug(f"Rejecting {det.issue_class} due to low confidence ({det.confidence:.2f})")
            continue
            
        # Check civic ontology
        if det.issue_class.lower() not in settings.civic_issue_classes:
            logger.debug(f"Rejecting {det.issue_class} as it is not a recognized civic issue.")
            continue
            
        valid_civic_issues.append(det)
        
    if not valid_civic_issues:
        logger.info("No valid civic issues detected in the image.")
        return None, [], "no_civic_issue_detected"
        
    # 2. Sort by confidence descending
    valid_civic_issues.sort(key=lambda d: d.confidence, reverse=True)
    
    # 3. Select primary and secondary
    primary_issue = valid_civic_issues[0]
    secondary_issues = valid_civic_issues[1:]
    
    return primary_issue, secondary_issues, "valid_civic_issue"

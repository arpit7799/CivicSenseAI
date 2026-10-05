# =============================================================================
# CivicSense AI — Image Preprocessing & Quality Assessment
# =============================================================================
# Owner: Arpit (Person 1)
# =============================================================================

import cv2
import numpy as np
import httpx

from app.config import get_settings
from app.contracts.vision import ImageQuality
from app.core.logging import get_logger
from app.core.errors import ImageValidationError

logger = get_logger(__name__)


async def download_image(url: str) -> bytes:
    """Download an image from a URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
    except httpx.HTTPError as e:
        raise ImageValidationError(f"Failed to download image: {e}")


def assess_and_decode_image(image_bytes: bytes) -> tuple[np.ndarray, ImageQuality]:
    """
    Decode image bytes and assess quality (resolution, blur).
    Returns the BGR image array and the ImageQuality contract.
    """
    settings = get_settings()
    
    # 1. Decode Image
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ImageValidationError("Failed to decode image — invalid format or corrupted")
        
    issues = []
    h, w, _ = image.shape
    
    # 2. Resolution Check
    resolution_adequate = True
    if w < settings.min_image_width or h < settings.min_image_height:
        resolution_adequate = False
        issues.append(f"low_resolution_({w}x{h})")
        
    # 3. Blur Detection (Variance of Laplacian)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Map variance to a 0.0-1.0 blur score (heuristic)
    # Lower variance means more blurry. We scale it so lower variance -> higher blur_score.
    # If variance = threshold, score = 0.5. 
    # If variance > threshold * 2, score approaches 0.
    # If variance < threshold / 2, score approaches 1.0.
    blur_score = max(0.0, min(1.0, 1.0 - (laplacian_var / (settings.blur_variance_threshold * 2))))
    
    if laplacian_var < settings.blur_variance_threshold:
        issues.append("too_blurry")
        
    # 4. Basic Brightness (check for completely black or blown out)
    mean_brightness = np.mean(gray)
    if mean_brightness < 15:
        issues.append("too_dark")
    elif mean_brightness > 240:
        issues.append("too_bright")
        
    # 5. Compile Quality Result
    is_valid = resolution_adequate and len(issues) == 0
    # A simple overall quality score
    quality_score = 1.0 - (blur_score * 0.5) - (0.2 if not resolution_adequate else 0.0) - (0.1 * len(issues))
    quality_score = max(0.0, min(1.0, quality_score))

    quality = ImageQuality(
        is_valid=is_valid,
        resolution_adequate=resolution_adequate,
        blur_score=blur_score,
        overall_quality_score=quality_score,
        issues=issues,
    )
    
    logger.debug(f"Image decoded: {w}x{h}, blur_var={laplacian_var:.1f}, valid={is_valid}")
    
    return image, quality

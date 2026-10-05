# =============================================================================
# CivicSense AI — Vision Tests
# =============================================================================

import pytest
import numpy as np
import cv2

from app.vision.preprocessing import assess_and_decode_image
from app.contracts.vision import ImageQuality

def test_assess_valid_image():
    # Create a 100x100 white image (valid resolution)
    img = np.ones((100, 100, 3), dtype=np.uint8) * 200
    # Add some noise to increase variance so it's not marked as blurry
    noise = np.random.randint(0, 50, (100, 100, 3), dtype=np.uint8)
    img = cv2.add(img, noise)
    
    # Encode to bytes
    success, encoded = cv2.imencode('.jpg', img)
    assert success
    
    bgr, quality = assess_and_decode_image(encoded.tobytes())
    
    assert bgr is not None
    assert bgr.shape == (100, 100, 3)
    assert isinstance(quality, ImageQuality)
    assert quality.resolution_adequate is True
    # The random noise should give enough variance to pass blur check
    assert "too_blurry" not in quality.issues


def test_assess_low_resolution():
    # Create a 32x32 image (below default 64x64 threshold)
    img = np.ones((32, 32, 3), dtype=np.uint8) * 128
    noise = np.random.randint(0, 50, (32, 32, 3), dtype=np.uint8)
    img = cv2.add(img, noise)
    
    success, encoded = cv2.imencode('.jpg', img)
    
    bgr, quality = assess_and_decode_image(encoded.tobytes())
    
    assert quality.resolution_adequate is False
    assert any("low_resolution" in issue for issue in quality.issues)
    assert quality.is_valid is False


def test_assess_blurry_image():
    # Create an image that is completely smooth (variance = 0)
    img = np.ones((100, 100, 3), dtype=np.uint8) * 128
    
    success, encoded = cv2.imencode('.jpg', img)
    
    bgr, quality = assess_and_decode_image(encoded.tobytes())
    
    assert "too_blurry" in quality.issues
    assert quality.is_valid is False
    assert quality.blur_score == 1.0


def test_assess_dark_image():
    # Create a very dark image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    
    success, encoded = cv2.imencode('.jpg', img)
    
    bgr, quality = assess_and_decode_image(encoded.tobytes())
    
    assert "too_dark" in quality.issues
    assert quality.is_valid is False


def test_assess_bright_image():
    # Create a completely white image
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    
    success, encoded = cv2.imencode('.jpg', img)
    
    bgr, quality = assess_and_decode_image(encoded.tobytes())
    
    assert "too_bright" in quality.issues
    assert quality.is_valid is False

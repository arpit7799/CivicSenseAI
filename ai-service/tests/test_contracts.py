# =============================================================================
# CivicSense AI — Contract Validation Tests
# =============================================================================
# Tests that Pydantic schemas validate correctly and reject invalid data.
# =============================================================================

import pytest
from pydantic import ValidationError

from app.contracts.vision import BoundingBox, Detection, ImageQuality, VisionResult
from app.contracts.severity import SeverityResult
from app.contracts.location import Coordinates, LocationResult
from app.contracts.authority import AuthorityResult
from app.contracts.complaint import ComplaintResult
from app.contracts.duplicate import DuplicateResult
from app.contracts.analysis import AnalysisRequest


class TestAnalysisRequest:
    """Tests for AnalysisRequest validation."""

    def test_valid_request(self):
        req = AnalysisRequest(
            image_url="https://example.com/test.jpg",
            latitude=28.4595,
            longitude=77.0266,
            user_description="Test description",
        )
        assert req.image_url == "https://example.com/test.jpg"
        assert req.latitude == 28.4595

    def test_optional_description(self):
        req = AnalysisRequest(
            image_url="https://example.com/test.jpg",
            latitude=28.4595,
            longitude=77.0266,
        )
        assert req.user_description is None

    def test_rejects_empty_image_url(self):
        with pytest.raises(ValidationError):
            AnalysisRequest(
                image_url="",
                latitude=28.4595,
                longitude=77.0266,
            )

    def test_rejects_latitude_out_of_range(self):
        with pytest.raises(ValidationError):
            AnalysisRequest(
                image_url="https://example.com/test.jpg",
                latitude=100.0,
                longitude=77.0266,
            )

    def test_rejects_longitude_out_of_range(self):
        with pytest.raises(ValidationError):
            AnalysisRequest(
                image_url="https://example.com/test.jpg",
                latitude=28.4595,
                longitude=200.0,
            )


class TestSeverityResult:
    """Tests for SeverityResult validation."""

    def test_valid_severity(self):
        result = SeverityResult(
            level="HIGH",
            score=0.86,
            factors=["large_damage_area"],
            confidence=0.9,
            source="mock",
        )
        assert result.level == "HIGH"

    def test_rejects_invalid_level(self):
        with pytest.raises(ValidationError):
            SeverityResult(
                level="EXTREME",  # Not a valid literal
                score=0.86,
                factors=[],
                confidence=0.9,
            )

    def test_rejects_score_above_one(self):
        with pytest.raises(ValidationError):
            SeverityResult(
                level="HIGH",
                score=1.5,
                factors=[],
                confidence=0.9,
            )

    def test_rejects_negative_confidence(self):
        with pytest.raises(ValidationError):
            SeverityResult(
                level="LOW",
                score=0.3,
                factors=[],
                confidence=-0.1,
            )


class TestLocationResult:
    """Tests for LocationResult validation."""

    def test_valid_location(self):
        result = LocationResult(
            address="123 Test Road",
            city="Test City",
            district="Test District",
            state="Test State",
            coordinates=Coordinates(latitude=28.4595, longitude=77.0266),
            confidence=0.95,
            source="mock",
        )
        assert result.ward is None  # Optional
        assert result.pincode is None  # Optional

    def test_optional_fields_accepted(self):
        result = LocationResult(
            address="123 Test Road",
            city="Test City",
            district="Test District",
            state="Test State",
            ward="Ward 5",
            zone="Zone A",
            pincode="110001",
            coordinates=Coordinates(latitude=28.4595, longitude=77.0266),
            confidence=0.95,
            source="geocoding_api",
        )
        assert result.ward == "Ward 5"
        assert result.pincode == "110001"

    def test_rejects_invalid_coordinates(self):
        with pytest.raises(ValidationError):
            Coordinates(latitude=100.0, longitude=77.0266)


class TestAuthorityResult:
    """Tests for AuthorityResult validation."""

    def test_valid_authority_with_contacts(self):
        result = AuthorityResult(
            authority_name="Municipal Corporation",
            department="Public Works",
            jurisdiction="City X",
            contact_email="pwd@muncorp.gov.in",
            confidence=0.9,
            source="verified_dataset",
            verified_at="2024-01-15T10:00:00Z",
        )
        assert result.source == "verified_dataset"

    def test_mock_authority_has_no_contacts(self):
        """Mock authority should have null contacts and null verified_at."""
        result = AuthorityResult(
            authority_name="Mock Authority",
            department="Mock Dept",
            jurisdiction="Mock",
            confidence=0.0,
            source="mock",
        )
        assert result.contact_email is None
        assert result.contact_phone is None
        assert result.verified_at is None


class TestComplaintResult:
    """Tests for ComplaintResult validation."""

    def test_valid_complaint(self):
        result = ComplaintResult(
            subject="Pothole Report",
            body="Dear Sir/Madam...",
            priority="HIGH",
            generated_at="2024-01-15T10:00:00Z",
            source="mock",
        )
        assert result.priority == "HIGH"

    def test_rejects_invalid_priority(self):
        with pytest.raises(ValidationError):
            ComplaintResult(
                subject="Test",
                body="Test body",
                priority="URGENT",  # Not a valid literal
                generated_at="2024-01-15T10:00:00Z",
            )


class TestDuplicateResult:
    """Tests for DuplicateResult validation."""

    def test_no_duplicate(self):
        result = DuplicateResult(
            is_potential_duplicate=False,
            similarity_score=0.0,
            source="mock",
        )
        assert result.existing_complaint_id is None

    def test_duplicate_found(self):
        result = DuplicateResult(
            is_potential_duplicate=True,
            existing_complaint_id="COMP-12345",
            similarity_score=0.89,
            match_factors=["gps_proximity", "same_issue_type"],
            source="duplicate_engine_v1",
        )
        assert result.similarity_score == 0.89


class TestVisionResult:
    """Tests for VisionResult and related schemas."""

    def test_valid_detection(self):
        detection = Detection(
            issue_class="pothole",
            confidence=0.94,
            bounding_box=BoundingBox(x_min=10, y_min=20, x_max=100, y_max=200),
        )
        assert detection.confidence == 0.94

    def test_rejects_confidence_above_one(self):
        with pytest.raises(ValidationError):
            Detection(
                issue_class="pothole",
                confidence=1.5,
                bounding_box=BoundingBox(x_min=10, y_min=20, x_max=100, y_max=200),
            )

    def test_image_quality(self):
        quality = ImageQuality(
            is_valid=True,
            resolution_adequate=True,
            blur_score=0.1,
            overall_quality_score=0.9,
            issues=[],
        )
        assert quality.is_valid is True

    def test_image_quality_with_issues(self):
        quality = ImageQuality(
            is_valid=False,
            resolution_adequate=False,
            blur_score=0.8,
            overall_quality_score=0.3,
            issues=["too_blurry", "low_resolution"],
        )
        assert len(quality.issues) == 2

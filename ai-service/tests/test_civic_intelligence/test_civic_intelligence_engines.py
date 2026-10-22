from datetime import datetime, timedelta, timezone

import pytest

from app.analytics.engine import CivicHotspotAnalyzer, CivicTrendAnalyzer
from app.contracts.civic_record import ComplaintObservation
from app.core.complaint_repository import ComplaintQuery
from app.duplicate.engine import CivicDuplicateDetector, haversine_meters


NOW = datetime(2026, 10, 22, 12, 0, tzinfo=timezone.utc)


class StubComplaintRepository:
    def __init__(self, records):
        self.records = records
        self.last_query = None

    async def list_complaints(self, query: ComplaintQuery):
        self.last_query = query
        result = self.records
        if query.issue_type:
            result = [r for r in result if r.issue_type.casefold() == query.issue_type.casefold()]
        if query.start_at:
            result = [r for r in result if r.reported_at >= query.start_at]
        if query.end_at:
            result = [r for r in result if r.reported_at <= query.end_at]
        if query.region:
            region = query.region.casefold()
            result = [
                r for r in result
                if region in {
                    value.casefold()
                    for value in (r.city, r.district, r.ward, r.zone)
                    if value
                }
            ]
        if query.radius_meters is not None:
            result = [
                r for r in result
                if haversine_meters(query.latitude, query.longitude, r.latitude, r.longitude)
                <= query.radius_meters
            ]
        return result


def complaint(
    complaint_id,
    *,
    issue="pothole",
    latitude=28.4595,
    longitude=77.0266,
    days_ago=1,
    description="Large pothole near the market",
    severity="HIGH",
    city="Gurugram",
):
    return ComplaintObservation(
        complaint_id=complaint_id,
        issue_type=issue,
        reported_at=NOW - timedelta(days=days_ago),
        latitude=latitude,
        longitude=longitude,
        description=description,
        severity=severity,
        city=city,
    )


@pytest.mark.anyio
async def test_duplicate_detector_explains_close_matching_report():
    prior = complaint("C-101", latitude=28.45951, description="Large pothole by market")
    repository = StubComplaintRepository([prior])
    detector = CivicDuplicateDetector(repository, clock=lambda: NOW)

    result = await detector.check(
        "POTHOLE", 28.4595, 77.0266, description="Large pothole near market"
    )

    assert result.is_potential_duplicate is True
    assert result.existing_complaint_id == "C-101"
    assert result.similarity_score > 0.65
    assert set(result.match_factors) == {
        "same_issue_type",
        "gps_proximity",
        "reported_within_time_window",
        "description_similarity",
    }
    assert repository.last_query.issue_type == "pothole"
    assert repository.last_query.radius_meters == 250.0


@pytest.mark.anyio
async def test_duplicate_detector_rejects_far_old_or_different_category_reports():
    repository = StubComplaintRepository(
        [
            complaint("far", latitude=28.4700),
            complaint("old", days_ago=31),
            complaint("other", issue="garbage_dump"),
        ]
    )
    detector = CivicDuplicateDetector(repository, clock=lambda: NOW)
    result = await detector.check("pothole", 28.4595, 77.0266)

    assert result.is_potential_duplicate is False
    assert result.existing_complaint_id is None
    assert result.similarity_score == 0.0


@pytest.mark.anyio
async def test_near_but_low_similarity_report_is_not_flagged():
    repository = StubComplaintRepository([complaint("near", latitude=28.4604, description=None)])
    detector = CivicDuplicateDetector(repository, clock=lambda: NOW)
    result = await detector.check("pothole", 28.4595, 77.0266)

    assert result.is_potential_duplicate is False
    assert result.existing_complaint_id is None
    assert "gps_proximity" in result.match_factors


@pytest.mark.anyio
async def test_hotspot_analyzer_returns_dense_cluster_not_noise():
    reports = [
        complaint("A", latitude=28.45950, longitude=77.02660),
        complaint("B", latitude=28.45955, longitude=77.02662, issue="road_damage", severity="MEDIUM"),
        complaint("C", latitude=28.45948, longitude=77.02668, issue="pothole", severity="HIGH"),
        complaint("noise", latitude=28.4630, longitude=77.0300),
    ]
    repository = StubComplaintRepository(reports)
    analyzer = CivicHotspotAnalyzer(repository, cluster_radius_meters=250, min_samples=3)
    result = await analyzer.analyze(28.4595, 77.0266, radius_km=1)

    assert result.source == "dbscan_haversine_v1"
    assert result.total_complaints_analyzed == 4
    assert len(result.clusters) == 1
    cluster = result.clusters[0]
    assert cluster.complaint_count == 3
    assert cluster.dominant_issue_type == "pothole"
    assert cluster.severity_distribution == {"HIGH": 2, "MEDIUM": 1}


@pytest.mark.anyio
async def test_trend_analyzer_uses_time_buckets_and_reports_direction():
    reports = [
        complaint(f"T-{index}", days_ago=6 - index, description=None)
        for index in range(1, 7)
    ]
    repository = StubComplaintRepository(reports)
    analyzer = CivicTrendAnalyzer(repository, clock=lambda: NOW)
    result = await analyzer.analyze("pothole", "Gurugram", time_window_days=7)

    assert result.source == "time_series_v1"
    assert result.trend_direction == "increasing"
    assert len(result.data_points) == 7
    assert sum(point.count for point in result.data_points) == 6
    assert result.data_points[-1].dominant_severity == "HIGH"


def test_complaint_observation_requires_timezone_aware_timestamp():
    with pytest.raises(ValueError, match="timezone"):
        ComplaintObservation(
            complaint_id="bad-time",
            issue_type="pothole",
            reported_at=datetime(2026, 10, 22),
            latitude=28.4595,
            longitude=77.0266,
        )

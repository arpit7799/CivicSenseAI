"""Spatial complaint clustering and time-window trend analysis."""

from collections import Counter
from datetime import datetime, timedelta, timezone

from app.contracts.analytics import (
    HotspotCluster,
    HotspotResult,
    TrendDataPoint,
    TrendResult,
)
from app.contracts.civic_record import ComplaintObservation
from app.contracts.location import Coordinates
from app.core.complaint_repository import ComplaintQuery, ComplaintRepository
from app.core.interfaces import HotspotAnalyzer, TrendAnalyzer
from app.duplicate.engine import haversine_meters


class CivicHotspotAnalyzer(HotspotAnalyzer):
    def __init__(
        self,
        repository: ComplaintRepository,
        *,
        cluster_radius_meters: float = 250.0,
        min_samples: int = 3,
    ):
        self.repository = repository
        self.cluster_radius_meters = cluster_radius_meters
        self.min_samples = min_samples

    async def analyze(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        issue_type: str | None = None,
    ) -> HotspotResult:
        complaints = await self.repository.list_complaints(
            ComplaintQuery(
                latitude=latitude,
                longitude=longitude,
                radius_meters=radius_km * 1000,
                issue_type=issue_type.casefold() if issue_type else None,
            )
        )
        groups = dbscan_clusters(
            complaints,
            epsilon_meters=self.cluster_radius_meters,
            min_samples=self.min_samples,
        )

        clusters = []
        for index, group in enumerate(groups, start=1):
            center_lat = sum(item.latitude for item in group) / len(group)
            center_lon = sum(item.longitude for item in group) / len(group)
            issue_counts = Counter(item.issue_type for item in group)
            severity_counts = Counter(item.severity for item in group if item.severity)
            clusters.append(
                HotspotCluster(
                    cluster_id=f"HOTSPOT-{index:03d}",
                    center=Coordinates(latitude=center_lat, longitude=center_lon),
                    radius_meters=max(
                        haversine_meters(center_lat, center_lon, item.latitude, item.longitude)
                        for item in group
                    ),
                    complaint_count=len(group),
                    dominant_issue_type=issue_counts.most_common(1)[0][0],
                    severity_distribution=dict(severity_counts),
                )
            )

        return HotspotResult(
            clusters=clusters,
            total_complaints_analyzed=len(complaints),
            analysis_region=f"{radius_km:g} km around ({latitude:.5f}, {longitude:.5f})",
            source="dbscan_haversine_v1",
        )


class CivicTrendAnalyzer(TrendAnalyzer):
    def __init__(self, repository: ComplaintRepository, *, clock=None):
        self.repository = repository
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    async def analyze(
        self,
        issue_type: str,
        region: str,
        time_window_days: int = 30,
    ) -> TrendResult:
        now = self._clock().astimezone(timezone.utc)
        start_at = now - timedelta(days=time_window_days)
        complaints = await self.repository.list_complaints(
            ComplaintQuery(
                start_at=start_at,
                end_at=now,
                issue_type=issue_type.casefold(),
                region=region,
            )
        )

        period_days = 1 if time_window_days < 14 else 7
        period_count = max(1, (time_window_days + period_days - 1) // period_days)
        grouped: list[list[ComplaintObservation]] = [[] for _ in range(period_count)]
        for complaint in complaints:
            elapsed_days = max(0.0, (complaint.reported_at - start_at).total_seconds() / 86400)
            index = min(period_count - 1, int(elapsed_days // period_days))
            grouped[index].append(complaint)

        data_points = []
        counts = []
        for index, group in enumerate(grouped):
            bucket_start = start_at + timedelta(days=index * period_days)
            period_label = bucket_start.date().isoformat()
            severity_counts = Counter(item.severity for item in group if item.severity)
            data_points.append(
                TrendDataPoint(
                    period=period_label,
                    count=len(group),
                    dominant_severity=severity_counts.most_common(1)[0][0] if severity_counts else None,
                )
            )
            counts.append(len(group))

        return TrendResult(
            issue_type=issue_type,
            trend_direction=classify_trend(counts),
            data_points=data_points,
            time_window_days=time_window_days,
            region=region,
            source="time_series_v1",
        )


def dbscan_clusters(
    complaints: list[ComplaintObservation],
    *,
    epsilon_meters: float,
    min_samples: int,
) -> list[list[ComplaintObservation]]:
    """Small, deterministic DBSCAN implementation using Haversine distance."""
    if epsilon_meters <= 0 or min_samples < 1:
        raise ValueError("epsilon_meters must be positive and min_samples must be at least one")
    neighbors = [
        [
            j
            for j, other in enumerate(complaints)
            if haversine_meters(item.latitude, item.longitude, other.latitude, other.longitude)
            <= epsilon_meters
        ]
        for item in complaints
    ]
    visited: set[int] = set()
    assigned: set[int] = set()
    clusters: list[list[ComplaintObservation]] = []

    for point_index in range(len(complaints)):
        if point_index in visited:
            continue
        visited.add(point_index)
        point_neighbors = neighbors[point_index]
        if len(point_neighbors) < min_samples:
            continue

        cluster_indices: list[int] = []
        queue = list(point_neighbors)
        queued = set(queue)
        cursor = 0
        while cursor < len(queue):
            candidate = queue[cursor]
            cursor += 1
            if candidate not in visited:
                visited.add(candidate)
                candidate_neighbors = neighbors[candidate]
                if len(candidate_neighbors) >= min_samples:
                    for neighbor_index in candidate_neighbors:
                        if neighbor_index not in queued:
                            queued.add(neighbor_index)
                            queue.append(neighbor_index)
            if candidate not in assigned:
                assigned.add(candidate)
                cluster_indices.append(candidate)
        clusters.append([complaints[index] for index in cluster_indices])
    return clusters


def classify_trend(counts: list[int]) -> str:
    if len(counts) < 2 or not any(counts):
        return "stable"
    active_periods = sum(count > 0 for count in counts)
    peaks = sum(
        counts[index] > counts[index - 1] and counts[index] >= counts[index + 1]
        for index in range(1, len(counts) - 1)
    )
    if active_periods >= 3 and peaks >= 2:
        return "recurring"

    midpoint = max(1, len(counts) // 2)
    first_half = sum(counts[:midpoint])
    second_half = sum(counts[midpoint:])
    if second_half > first_half * 1.2:
        return "increasing"
    if second_half < first_half * 0.8:
        return "decreasing"
    return "stable"

from datetime import datetime, timezone

import pytest

from app.core.complaint_repository import ComplaintQuery
from app.core.postgres_complaint_repository import PostgresComplaintRepository


class FakePool:
    def __init__(self, rows):
        self.rows = rows
        self.query = None
        self.args = None

    async def fetch(self, query, *args):
        self.query = query
        self.args = args
        return self.rows


@pytest.mark.anyio
async def test_postgres_repository_builds_parameterized_spatial_query():
    pool = FakePool([
        {
            "complaint_id": "APP-1",
            "issue_type": "pothole",
            "reported_at": datetime(2026, 10, 22, tzinfo=timezone.utc),
            "latitude": 28.4595,
            "longitude": 77.0266,
            "severity": "HIGH",
            "description": "Road damage",
            "image_ref": None,
            "city": "Gurugram",
            "district": "Gurugram",
            "state": "Haryana",
            "ward": None,
            "zone": None,
        }
    ])
    repository = PostgresComplaintRepository(pool=pool)
    start_at = datetime(2026, 10, 1, tzinfo=timezone.utc)
    rows = await repository.list_complaints(
        ComplaintQuery(
            start_at=start_at,
            issue_type="POTHOLE",
            region="Gurugram' OR TRUE --",
            latitude=28.4595,
            longitude=77.0266,
            radius_meters=250,
        )
    )

    assert len(rows) == 1
    assert rows[0].complaint_id == "APP-1"
    assert "$1" in pool.query and "$2" in pool.query and "$3" in pool.query
    assert "ST_DWithin(location::geography" in pool.query
    assert pool.args == (
        start_at,
        "pothole",
        "gurugram' or true --",
        77.0266,
        28.4595,
        250,
    )
    assert "Gurugram' OR TRUE --" not in pool.query

# CivicSense AI data model

## Stage 2 decisions

- PostgreSQL with PostGIS is the persistence and spatial-query layer.
- The main application remains the system of record for complaint lifecycle,
  citizen identity, submission, status, and notifications.
- The AI service receives complaint data from the main application through an
  API-fed, read-optimized complaint index. This avoids a shared-database
  dependency while keeping the main application as the system of record.
- Authority and department records are civic-intelligence data owned by the
  AI service. Contact details are usable only when their source and verification
  date are present and the record is marked verified.
- Store latitude and longitude in WGS84 and a PostGIS point for spatial
  indexing; cast it to geography for meter-based radius searches. Preserve the
  original coordinates even when reverse geocoding is incomplete.
- Initial jurisdiction for implementation: Gurugram, Haryana, matching the
  project's example coordinates. Keep city and district fields explicit so
  this can expand to additional jurisdictions without changing the API.

## Complaint index

The main application owns complaint lifecycle. It sends the following
projection to the AI service when a report is created or updated, for duplicate
checks, hotspots, and trends:

| Field | Type | Required | Purpose |
|---|---|---:|---|
| `complaint_id` | string | Yes | Stable ID assigned by the main application |
| `issue_type` | string | Yes | Canonical civic issue category |
| `reported_at` | timestamp with time zone | Yes | Time used by duplicate windows and trend buckets |
| `latitude`, `longitude` | decimal | Yes | Original WGS84 coordinates |
| `location` | PostGIS `geometry(Point, 4326)` | Yes | GiST index; cast to geography for meter-based distance queries |
| `severity` | enum/string | No | LOW, MEDIUM, HIGH, or CRITICAL |
| `description` | text | No | Used for text similarity |
| `image_ref` | string | No | Application-owned image reference; no image bytes in this index |
| `city`, `district`, `state`, `ward`, `zone` | string | Optional | Normalized jurisdiction filters |

The index must be refreshable from the application source of truth. The AI
service does not create or change complaint status. Duplicate results point
back to `complaint_id` and remain advisory for citizen review.

Required indexes: primary key on `complaint_id`, GiST on `location`, and
composite B-tree indexes on `(issue_type, reported_at)` and jurisdiction plus
`reported_at` for analytics filters.

## Verified authority records

Authority records are maintained separately from complaints. Each record
contains:

- Stable record ID and authority name.
- Department and canonical issue types handled.
- Jurisdiction type and name, with normalized city, district, state, ward,
  and/or zone fields where available.
- Official contact fields, each nullable.
- Source URL or document reference.
- Verification status and `verified_at` timestamp.
- Active flag and optional route priority for overlapping responsibilities.

Routing matches issue type and the most specific available jurisdiction.
Unverified or missing records may be returned as unresolved metadata, but
their contacts must not be passed to complaint generation as official values.

## API boundary

Keep existing Pydantic contracts as the AI service boundary. The main
application syncs complaint projections using stable complaint IDs; duplicate
and analytics providers query the local index. Authority data stays behind
`AuthorityProvider`; callers receive `AuthorityResult`, including provenance
and confidence. The first authority dataset is a sourced JSON file that can
move to PostgreSQL when the data-maintenance workflow is ready.

The API-fed projection is the chosen MVP boundary. The main application writes
complaints; the AI service accepts idempotent index upserts and may rebuild its
index from the main application if local index data is lost. Do not make the AI
service the authority for complaint status or submission state.

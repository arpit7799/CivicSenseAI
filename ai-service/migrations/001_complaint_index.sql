-- Read-optimized projection of main-application complaints for AI services.
-- The main application remains the source of truth for complaint lifecycle.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS civic_complaint_index (
    complaint_id TEXT PRIMARY KEY,
    issue_type TEXT NOT NULL CHECK (length(trim(issue_type)) > 0),
    reported_at TIMESTAMPTZ NOT NULL,
    latitude DOUBLE PRECISION NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude DOUBLE PRECISION NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    location geometry(Point, 4326)
        GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)) STORED,
    severity TEXT CHECK (severity IS NULL OR severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    description TEXT,
    image_ref TEXT,
    city TEXT,
    district TEXT,
    state TEXT,
    ward TEXT,
    zone TEXT,
    indexed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS civic_complaint_index_location_gix
    ON civic_complaint_index USING GIST (location);

CREATE INDEX IF NOT EXISTS civic_complaint_index_issue_reported_idx
    ON civic_complaint_index (issue_type, reported_at DESC);

CREATE INDEX IF NOT EXISTS civic_complaint_index_city_reported_idx
    ON civic_complaint_index (lower(city), reported_at DESC);

CREATE INDEX IF NOT EXISTS civic_complaint_index_district_reported_idx
    ON civic_complaint_index (lower(district), reported_at DESC);

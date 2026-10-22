# CivicSense AI

**AI-Powered Civic Complaint Detection, Generation & Routing Platform**

---

## Project Overview

CivicSense AI simplifies civic complaint reporting. A citizen captures a photo of a civic issue (pothole, garbage, broken streetlight, etc.) with location context. The AI system:

1. **Detects** the civic issue from the photograph
2. **Classifies** the issue type with confidence scores
3. **Estimates** severity (LOW / MEDIUM / HIGH / CRITICAL)
4. **Resolves** the geographic location and jurisdiction
5. **Identifies** the responsible authority and department
6. **Retrieves** relevant civic knowledge via RAG
7. **Generates** a structured, professional complaint
8. **Checks** for duplicate complaints
9. **Presents** the complaint for citizen review and submission

---

## Architecture

```
CITIZEN → PHOTO + GPS
       ↓
   NEXT.JS FRONTEND
       ↓
   MAIN FASTAPI BACKEND
       ↓
   AI SERVICE (FastAPI)
       ↓
   ┌─────────────────────────────────────────────┐
   │              AI ENGINE                      │
   │                                             │
   │  ┌─────────────┐    ┌───────────────────┐   │
   │  │ PERSON 1     │    │ PERSON 2          │   │
   │  │ (Arpit)      │    │ (Arnav)           │   │
   │  │              │    │                   │   │
   │  │ Vision       │    │ Location          │   │
   │  │ Severity     │    │ Authority         │   │
   │  │ RAG          │    │ Duplicate         │   │
   │  │ LLM          │    │ Hotspots          │   │
   │  │ Decision     │    │ Trends            │   │
   │  └──────┬───────┘    └────────┬──────────┘   │
   │         └──────────┬──────────┘              │
   │                    ↓                         │
   │          STRUCTURED RESULT                   │
   └─────────────────────────────────────────────┘
       ↓
   USER REVIEW → SUBMISSION → AUTHORITY → TRACKING
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Main Backend | Python, FastAPI |
| Database | PostgreSQL |
| Caching | Redis |
| Computer Vision | PyTorch, Ultralytics YOLO, OpenCV |
| Machine Learning | Scikit-learn |
| NLP / LLM | Transformers, Ollama |
| Embeddings | BGE |
| Vector Database | Qdrant |
| Containerization | Docker |
| Version Control | Git / GitHub |

---

## Team Ownership

| Module | Owner | Description |
|---|---|---|
| `ai-service/app/vision/` | **Arpit** | Image preprocessing, YOLO detection, classification |
| `ai-service/app/severity/` | **Arpit** | Severity assessment engine |
| `ai-service/app/decision/` | **Arpit** | Core AI decision orchestration |
| `ai-service/app/rag/` | **Arpit** | BGE embeddings, Qdrant retrieval, RAG pipeline |
| `ai-service/app/llm/` | **Arpit** | Ollama integration, prompt architecture, complaint generation |
| `ai-service/app/location/` | **Arnav** | Reverse geocoding, geographic normalization |
| `ai-service/app/authority/` | **Arnav** | Authority routing, verified civic dataset |
| `ai-service/app/duplicate/` | **Arnav** | Duplicate complaint detection |
| `ai-service/app/analytics/` | **Arnav** | Hotspot detection, trend analysis |
| `ai-service/app/contracts/` | **Shared** | Pydantic schemas — API contract |
| `ai-service/app/core/` | **Shared** | Interfaces, config, logging, errors |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/TDevViper/CivicSenseAI.git
cd CivicSenseAI

# 2. Create and activate a virtual environment (Python 3.10+)
python3 -m venv .venv
source .venv/bin/activate

# 3. Install API dependencies
pip install -r ai-service/requirements.txt

# Optional: install vision and RAG model dependencies
# pip install -r ai-service/requirements-ai.txt
# Optional: install the Postgres adapter dependency
# pip install -r ai-service/requirements-db.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run from the ai-service directory
cd ai-service
uvicorn app.main:app --reload

# 6. Run the test suite (install requirements-ai.txt first for model tests)
python -m pytest -q
```

The default `PROVIDER_MODE=mock` starts the API without downloading model
weights. The service exposes interactive API documentation at
`http://localhost:8000/docs` and health information at
`http://localhost:8000/api/v1/health`. Set `PROVIDER_MODE=production` only after
installing `requirements-ai.txt` and configuring the required model files and
services. Ollama must be installed and running separately for live LLM use.

Provider settings are independent: `LOCATION_PROVIDER` accepts `mock` or
`nominatim`; `AUTHORITY_PROVIDER` accepts `mock` or `verified_dataset`;
`DUPLICATE_PROVIDER` and `ANALYTICS_PROVIDER` accept `mock` or `engine`.
Engine-based duplicate and analytics providers read the complaint index.

Reverse geocoding is independently configured. Keep `LOCATION_PROVIDER=mock`
for offline development; set it to `nominatim` to enable the opt-in Nominatim
adapter. The public Nominatim service is limited to low-volume, user-triggered
lookups and requires an identifying User-Agent, request spacing, caching, and
OpenStreetMap attribution. Its result is the nearest suitable mapped object,
so the returned address can differ from the exact coordinate. See the
[Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/)
and [reverse API documentation](https://nominatim.org/release-docs/latest/api/Reverse/).
The request limiter and cache are process-local; use one worker for this public
endpoint or configure a provider suitable for multi-worker production traffic.

Verified authority routing is also independently configured. Set
`AUTHORITY_PROVIDER=verified_dataset` to use the sourced Gurugram starter record.
It resolves to MCG's general civic grievance channel; the dataset deliberately
leaves the issue-specific department unset because the source does not establish
that mapping. Check the record's verification date and source before relying on
it in a live deployment.

---

## API

All routes are under `/api/v1`:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Service and provider status |
| `POST /analyze` | Analyze a civic issue image and location |
| `POST /location/resolve` | Resolve coordinates to a location |
| `POST /authority/route` | Find a supported authority route |
| `POST /duplicate/check` | Check for likely duplicate complaints |
| `POST /analytics/hotspots` | Find complaint clusters |
| `POST /analytics/trends` | Summarize complaint trends |
| `POST /complaint-index/upsert` | Authenticated internal complaint sync |

See `/docs` for request and response schemas.

### Complaint index sync

The main backend owns complaint records and syncs a read-only projection to the
AI service. Configure a random `COMPLAINT_INDEX_API_KEY` and send it as a Bearer
token to `POST /api/v1/complaint-index/upsert`. The default in-memory repository
is for local development only and loses records on restart. For durable data,
install `ai-service/requirements-db.txt`, set `COMPLAINT_REPOSITORY=postgres`,
and apply `ai-service/migrations/001_complaint_index.sql` to a PostgreSQL
database with PostGIS installed.

Set `DUPLICATE_PROVIDER=engine` and `ANALYTICS_PROVIDER=engine` to use the
complaint-index-backed duplicate, hotspot, and trend implementations. Their
default remains mock mode until the application is syncing complaint records.

Example request:

```http
POST /api/v1/complaint-index/upsert
Authorization: Bearer <service-key>
Content-Type: application/json

{
  "records": [
    {
      "complaint_id": "APP-123",
      "issue_type": "pothole",
      "reported_at": "2026-10-22T10:00:00Z",
      "latitude": 28.4595,
      "longitude": 77.0266,
      "severity": "HIGH",
      "description": "Large pothole near the market",
      "city": "Gurugram",
      "state": "Haryana"
    }
  ]
}
```

### Health Check
```
GET /api/v1/health
```

### Analyze Civic Issue
```
POST /api/v1/analyze
Content-Type: application/json

{
    "image_url": "https://example.com/pothole.jpg",
    "latitude": 28.4595,
    "longitude": 77.0266,
    "user_description": "Large pothole on main road"
}
```

---

## Implementation Status

| Stage | Scope | Status |
|---|---|---|
| 1 | Service foundation and contracts | Implemented |
| 2 | Data model and complaint read projection | Implemented |
| 3 | Vision and severity pipeline integration | Existing pipeline; CivicSense model training pending labeled images |
| 4 | Location resolution | Mock and opt-in Nominatim providers implemented |
| 5 | Authority routing | Mock and sourced Gurugram starter record implemented |
| 6 | Civic knowledge / RAG | Pipeline and verified starter source implemented; live model/service setup required |
| 7 | Complaint generation | Existing pipeline; live Ollama integration requires local service/model |
| 8 | Duplicate detection and analytics | Engine implementations available against complaint index |
| 9 | API and database integration | Sync API and PostGIS adapter implemented; live database verification pending |
| 10 | End-to-end deployment verification | Pending live model, database, and deployment configuration |

The repository test suite has passed with 120 tests in the development
environment. Tests do not replace live verification of external services.
There is no CivicSense-labeled image dataset in the repository, so a project
specific YOLO model has not been trained. PostGIS, live Ollama, and downloaded
BGE inference need to be configured and verified in the target environment.

---

## License

This project is developed as part of an academic/professional collaboration.

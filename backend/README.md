# CivicSense AI — Backend Service

**High-Performance FastAPI Multimodal AI & Civic Intelligence Service**

The `backend/` directory contains the complete backend service for CivicSense AI. It exposes a unified REST API contract (`/api/v1`) that connects computer vision detection, multi-factor risk severity assessment, geographic intelligence, municipal authority routing, civic knowledge retrieval (RAG), and LLM complaint letter drafting.

---

## 1. Architecture & Pipeline Alignment

When a citizen submits a photograph and coordinates to `POST /api/v1/analyze`, the **Decision Engine** (`app/decision/engine.py`) orchestrates the pipeline through 6 modular phases:

```
[ Citizen Image + Coordinates ]
                │
                ▼
     ┌──────────────────────┐
     │ 1. Vision Engine     │ ➔ Preprocessing, blur score, YOLOv8 detection, ontology filter
     └──────────┬───────────┘
                │ (If no civic issue detected: short-circuits gracefully)
                ▼
     ┌──────────────────────┐
     │ 2. Severity Engine   │ ➔ Multi-factor scoring (damage size, obstruction, pedestrian risk)
     └──────────┬───────────┘
                ▼
     ┌──────────────────────┐
     │ 3. Geo & Authority   │ ➔ Reverse geocoding (Nominatim) + Verified municipal registry
     └──────────┬───────────┘
                ▼
     ┌──────────────────────┐
     │ 4. RAG Charter Check │ ➔ BGE embeddings + Qdrant vector search for statutory timelines
     └──────────┬───────────┘
                ▼
     ┌──────────────────────┐
     │ 5. Duplicate Check   │ ➔ Spatial proximity + semantic matching against active complaints
     └──────────┬───────────┘
                ▼
     ┌──────────────────────┐
     │ 6. LLM Complaint     │ ➔ Ollama Llama 3.2 municipal draft (with deterministic fallback)
     └──────────────────────┘
```

---

## 2. Directory Layout & Module Breakdown

```
backend/
├── app/
│   ├── main.py                  # FastAPI app factory, CORS middleware, lifespan events
│   ├── config.py                # Pydantic BaseSettings (env, model paths, provider toggles)
│   │
│   ├── contracts/               # Pydantic v2 schemas defining immutable API contracts
│   │   ├── analysis.py          # AnalysisRequest and AnalysisResponse schemas
│   │   ├── vision.py            # BoundingBox, Detection, ImageQuality, VisionResult
│   │   ├── severity.py          # SeverityResult, SeverityContributingFactor
│   │   ├── location.py          # Coordinates, LocationResult
│   │   ├── authority.py         # AuthorityResult (verified provenance fields)
│   │   ├── rag.py               # RAGResult, ContextDocument
│   │   ├── complaint.py         # ComplaintRequest, ComplaintResult
│   │   ├── duplicate.py         # DuplicateCheckRequest, DuplicateResult
│   │   └── analytics.py         # HotspotRequest, HotspotResult, TrendResult
│   │
│   ├── core/                    # Interfaces, logging, error handling, repositories
│   │   ├── interfaces.py        # Abstract base classes for all pluggable providers
│   │   ├── errors.py            # Typed domain exceptions (e.g. ImageValidationError)
│   │   ├── logging.py           # Structured JSON logger with request IDs
│   │   ├── memory_complaint_repository.py    # Local thread-safe in-memory store
│   │   └── postgres_complaint_repository.py  # Production PostGIS repository adapter
│   │
│   ├── vision/                  # Vision processing and object detection
│   │   ├── preprocessing.py     # Resize, aspect-ratio check, Laplacian blur detector
│   │   ├── detector.py          # Ultralytics YOLOv8 inference & base64 image parsing
│   │   ├── classifier.py        # Civic ontology mapper & confidence thresholding
│   │   └── mock_detector.py     # Lightweight mock for offline integration testing
│   │
│   ├── severity/                # Severity assessment engine
│   │   ├── engine.py            # Multi-factor algorithmic risk scoring engine
│   │   └── mock_engine.py       # Deterministic severity mock
│   │
│   ├── location/                # Geographic intelligence
│   │   ├── nominatim_provider.py # Reverse geocoder with rate-limiting & OSM attribution
│   │   └── mock_provider.py     # Offline geocoding mock
│   │
│   ├── authority/               # Civic authority routing
│   │   ├── dataset_provider.py  # Sourced municipal registry parser (verified provenance)
│   │   ├── authority_routes.json # Sourced Gurugram municipal directory
│   │   └── mock_provider.py     # Offline authority mock
│   │
│   ├── duplicate/               # Duplicate complaint detection
│   │   ├── engine.py            # Spatial distance & text similarity duplicate detector
│   │   └── mock_detector.py     # Offline duplicate mock
│   │
│   ├── analytics/               # Civic intelligence aggregation
│   │   ├── engine.py            # Spatial DBSCAN hotspot clustering and trends
│   │   └── mock_analyzer.py     # Offline analytics mock
│   │
│   ├── rag/                     # Civic knowledge retrieval
│   │   ├── retriever.py         # BGE-small embedding model & Qdrant vector retrieval
│   │   ├── ingestion.py         # Document chunker & vector collection indexer
│   │   └── mock_retriever.py    # Offline citizen charter mock
│   │
│   ├── llm/                     # Structured municipal complaint generation
│   │   ├── generator.py         # Prompt engineering & Ollama Llama 3.2 client
│   │   ├── fallback.py          # Rule-based template fallback when Ollama is offline
│   │   ├── guardrails.py        # Anti-hallucination sanitization & tone verifier
│   │   └── mock_generator.py    # Offline complaint generator mock
│   │
│   ├── decision/                # Pipeline orchestrator
│   │   └── engine.py            # Multimodal Decision Engine coordinating all stages
│   │
│   └── api/                     # REST API routing
│       ├── deps.py              # FastAPI dependency injection container
│       └── v1/
│           ├── router.py        # Sub-router aggregating all v1 endpoints
│           └── endpoints/       # Endpoint handlers (health, analyze, location, etc.)
│
├── datasets/                    # Civic vision dataset & training splits
├── models/                      # Fine-tuned YOLOv8 weights (civicsense_yolo.pt)
├── migrations/                  # PostgreSQL / PostGIS database schemas
├── scripts/                     # Dataset generators and model training scripts
└── tests/                       # Complete pytest test suite (129 tests)
```

---

## 3. Team Ownership Alignment

| Module | Component | Owner | Responsibilities |
|---|---|---|---|
| `app/vision/` | Computer Vision | **Arpit** | YOLOv8 training, inference, image quality, blur checking |
| `app/severity/` | Severity Engine | **Arpit** | Multi-factor risk calculation, priority matrix |
| `app/decision/` | Decision Engine | **Arpit** | Pipeline execution, short-circuit logic, error recovery |
| `app/rag/` | Civic RAG | **Arpit** | BGE embeddings, Qdrant vector retrieval, charter ingestion |
| `app/llm/` | Complaint Generator | **Arpit** | Ollama prompts, guardrails, deterministic fallback |
| `app/location/` | Geographic Intelligence | **Arnav** | Nominatim reverse geocoding, boundary mapping |
| `app/authority/` | Authority Routing | **Arnav** | Municipal directory, verified department mapping |
| `app/duplicate/` | Duplicate Detection | **Arnav** | Proximity radius checks, similarity calculation |
| `app/analytics/` | Hotspots & Trends | **Arnav** | Geospatial clustering, temporal trend summaries |
| `app/contracts/` | API Contracts | **Shared** | Immutable Pydantic v2 data transfer schemas |
| `app/core/` | Core Architecture | **Shared** | Abstract interfaces, logging, repositories |

---

## 4. API Endpoints Reference

All routes are mounted under `/api/v1`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service status, version, and provider modes (`mock` vs `configured`) |
| `POST` | `/api/v1/analyze` | Main citizen multimodal endpoint: vision, severity, geo, RAG, and LLM |
| `POST` | `/api/v1/location/resolve` | Reverse geocodes latitude/longitude coordinates |
| `POST` | `/api/v1/authority/route` | Resolves responsible municipal authority from city/ward |
| `POST` | `/api/v1/duplicate/check` | Evaluates if a complaint already exists near the coordinates |
| `POST` | `/api/v1/analytics/hotspots` | Returns civic defect density clusters within a radius |
| `POST` | `/api/v1/analytics/trends` | Returns temporal complaint trends for a given region |
| `POST` | `/api/v1/complaint-index/upsert` | Authenticated sync endpoint for syncing complaint records |

Interactive OpenAPI documentation is automatically served at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 5. Running the Backend

### 1. Activate Environment
```bash
source ../civicsenseAI_env/bin/activate
```

### 2. Start the Development Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The service will start on `http://127.0.0.1:8000`. CORS is pre-configured to allow connections from the Next.js frontend running on `http://localhost:3000`.

---

## 6. Running Tests

The test suite covers unit tests, contract validations, integration suites, and end-to-end pipeline executions:

```bash
pytest tests/ -v
```

**Test Status:** 129 passing tests in ~2.5 seconds.

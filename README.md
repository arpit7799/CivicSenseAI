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
git clone https://github.com/arpit7799/CivicSenseAI.git
cd CivicSenseAI

# 2. Create virtual environment
python3 -m venv civicsenseAI_env
source civicsenseAI_env/bin/activate

# 3. Install dependencies
pip install -r ai-service/requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run the AI service
cd ai-service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 6. Test
pytest tests/ -v
```

---

## API

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

## Development Roadmap

| Phase | Name | Status |
|---|---|---|
| Phase 1 | Foundation | 🔨 In Progress |
| Phase 2 | Computer Vision | ⏳ Pending |
| Phase 3 | Severity Intelligence | ⏳ Pending |
| Phase 4 | Location Intelligence (Arnav) | ⏳ Pending |
| Phase 5 | Authority Intelligence (Arnav) | ⏳ Pending |
| Phase 6 | RAG System | ⏳ Pending |
| Phase 7 | Complaint Intelligence | ⏳ Pending |
| Phase 8 | Advanced AI (Arnav) | ⏳ Pending |
| Phase 9 | Full Integration | ⏳ Pending |

---

## License

This project is developed as part of an academic/professional collaboration.

# SIH 26189 AI-Assisted Criminal Network Analysis System

An explainable, human-in-the-loop AI platform to extract, link, and visualize criminal networks for investigative support.

> [!IMPORTANT]
> **Synthetic Data & Safety Policy:** This repository strictly uses synthetic datasets. Under no circumstances are real police records, personal phone numbers, bank accounts, or personally identifiable data (PII) stored or processed. The system generates investigative leads and pattern visual representations; it **does NOT predict guilt, criminality, or automatically accuse individuals**.

---

## 1. Problem Context (SIH 26189)
Investigative agencies process heterogeneous evidence streams—unstructured text case reports, Call Detail Records (CDRs), financial transaction logs, vehicle sightings, and location logs. Manually linking these streams across cases is labor-intensive and prone to missed patterns. 

This platform provides an explainable AI assistant to:
1. Ingest synthetic multi-source case evidence.
2. Extract candidate entities (People, Aliases, Phone Numbers, Accounts, Vehicles, Locations, Organizations, Cases, Events).
3. Store relational state and audit trails in **PostgreSQL** and indexed graph structures in **Neo4j**.
4. Support human investigators with evidence snippets, timestamps, confidence scores, and **Human-in-the-Loop verification** (`ACCEPT`, `REJECT`, `CORRECT`).

---

## 2. Ethical Boundaries & System Rules
- **Synthetic Data Only:** All data streams are synthetically generated.
- **Investigative Leads:** Model outputs are marked as *investigative leads*, *patterns*, or *requiring human verification*.
- **No Guilt Prediction:** System scores indicate extraction confidence, never guilt.
- **Full Traceability:** Every link retains its source evidence text snippet and timestamp.
- **Human Authority:** Investigators retain full control to accept, reject, or edit model findings.

---

## 3. Repository Structure
```
d:/Sih/
├── AGENTS.md                  # Project rules & coding standards
├── docker-compose.yml         # Container setup for PostgreSQL 16 & Neo4j 5
├── .env.example               # Root environment variable template
├── pyproject.toml             # Root Python project & Pytest configuration
├── docs/                      ## Architecture & Documentation
- [Product Requirements](docs/product-requirements.md)
- [Architecture](docs/architecture.md)
- [Data Model](docs/data-model.md)
- [Graph Schema](docs/graph-schema.md)
- [Neo4j Development](docs/neo4j-development.md)
- [Synthetic Data Strategy](docs/synthetic-data.md)
- [Ingestion Pipeline](docs/ingestion-pipeline.md)
- [Graph Synchronization](docs/graph-sync.md)
- **docs/ingestion-pipeline.md**: Idempotent ETL processes.
- **docs/graph-analytics.md**: Engine architecture and fallback mechanisms.
- **docs/pattern-detection.md**: Deterministic suspicious lead generation.
- **docs/review-workflow.md**: Human-in-the-loop review state management.
- **docs/analytics-limitations.md**: System constraints and offline behaviors.
│   ├── graph-schema.md        # Neo4j Nodes and Relationships
│   ├── neo4j-development.md   # Local Neo4j Setup & Offline Behavior
│   └── risks-and-assumptions.md
├── apps/
│   ├── backend/               # Python FastAPI REST service
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── core/
│   │   │   └── api/v1/
│   │   ├── requirements.txt
│   │   └── .env.example
│   └── frontend/              # Next.js TypeScript strict-mode application
│       ├── app/               # Next.js App Router pages & layouts
│       ├── components/        # UI components & dashboard shell
│       └── package.json
├── packages/
│   └── shared/                # Shared schemas and data contracts
├── data/
│   └── synthetic/             # Synthetic case datasets
└── tests/                     # Automated backend integration tests
    └── backend/
```

---

## 4. Local Development Setup

### 4.1 Prerequisites
- **Python:** 3.10+
- **Node.js:** v22+ (with `npm` 10+)
- **Docker & Docker Compose:** Optional (Note: Docker CLI is currently unavailable in the local execution environment).

---

### 4.2 Backend Setup & Execution

1. Navigate to backend directory and create a Python virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment:
   - Windows PowerShell:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r apps/backend/requirements.txt
   ```
4. Copy the environment configuration:
   ```bash
   cp apps/backend/.env.example apps/backend/.env
   ```
5. Run the FastAPI development server:
   ```bash
   python -m uvicorn apps.backend.app.main:app --reload --port 8000
   ```
   Access API Health Check: `http://localhost:8000/api/v1/health`  
   Access Interactive Swagger Docs: `http://localhost:8000/docs`

---

### 4.3 Frontend Setup & Execution

1. Navigate to the frontend directory:
   ```bash
   cd apps/frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```
   Access Web Interface: `http://localhost:3000`

---

### 4.4 Automated Testing & Type Checking

- **Run Backend Unit & Integration Tests:**
  ```bash
  pytest -q tests/backend/test_health.py
  ```
- **Run Frontend TypeScript Type-Check:**
  ```bash
  cd apps/frontend && npm run type-check
  ```
- **Build Frontend Application:**
  ```bash
  cd apps/frontend && npm run build
  ```

---

### 4.5 Docker Infrastructure (PostgreSQL & Neo4j)

> [!NOTE]
> **Local Environment Limitation:** Docker CLI is currently unavailable on this machine. The backend service runs locally and returns structured responses. When deploying to environments with Docker installed, initialize database services using:

```bash
docker-compose up -d
```
- **PostgreSQL:** `localhost:5432`
- **Neo4j Browser:** `http://localhost:7474`
- **Neo4j Bolt:** `bolt://localhost:7687`

---

## 5. Current Milestone Limitations
- **Current Milestone:** Initial Project Scaffolding & Health Endpoints.
- **Pending Features:** PostgreSQL persistence, Neo4j graph synchronization, NLP entity extraction, Cytoscape graph visualization, and authentication will be added in subsequent milestones.

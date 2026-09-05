from fastapi import APIRouter

from apps.backend.app.api.v1.endpoints import cases, documents, health, graph, ingestion, analytics, similarity, ml, extraction, auth

api_v1_router = APIRouter()

# Authentication
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# System
api_v1_router.include_router(health.router, tags=["System Health"])

# ML Health
api_v1_router.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])

# Graph endpoints
api_v1_router.include_router(graph.router, tags=["Graph"])

# Ingestion endpoints (no prefix because paths are mixed /cases/, /documents/, /graph/sync/retry)
api_v1_router.include_router(ingestion.router, tags=["Ingestion"])

# Case management
api_v1_router.include_router(cases.router, prefix="/cases", tags=["Cases"])

# Case Machine Learning and Similarity (under /cases/ prefix natively, but registered without prefix if routes define /cases/{case_id})
api_v1_router.include_router(similarity.router, prefix="/cases", tags=["Similarity"])
api_v1_router.include_router(ml.router, prefix="/cases", tags=["Machine Learning Predictions"])

# Document management (nested under cases)
api_v1_router.include_router(
    documents.router,
    prefix="/cases/{case_id}/documents",
    tags=["Documents"],
)

# Placeholders for future milestone routers:
# api_v1_router.include_router(audit.router, prefix="/audit", tags=["Audit Logs"])

api_v1_router.include_router(analytics.router, tags=["Analytics"])
api_v1_router.include_router(extraction.router, tags=["Extraction"])

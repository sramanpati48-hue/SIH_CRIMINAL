"""API endpoints for ingestion and processing."""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session
import os

from apps.backend.app.db.session import get_db
from apps.backend.app.ingestion.service import IngestionService
from apps.backend.app.models.processing_job import ProcessingJob

router = APIRouter()

def get_ingestion_service(db: Session = Depends(get_db)) -> IngestionService:
    return IngestionService(db)

@router.post("/cases/{case_id}/upload", summary="Upload a file to a case")
async def upload_file(case_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a file (e.g. CSV, JSON) to a case."""
    if not file.filename.endswith(('.csv', '.json')):
        raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported.")
    # Real implementation would save this to cloud storage or disk, then return document_id.
    return {"message": "File uploaded successfully (mock).", "filename": file.filename}

@router.post("/cases/{case_id}/ingest-synthetic", summary="Ingest the generated synthetic dataset")
def ingest_synthetic(case_id: str, background_tasks: BackgroundTasks, service: IngestionService = Depends(get_ingestion_service)):
    """Trigger ingestion of the local synthetic dataset."""
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))), "data", "synthetic")
    if not os.path.exists(os.path.join(base_dir, "people.csv")):
        raise HTTPException(status_code=404, detail="Synthetic data not found. Run generate_data.py first.")
    
    # Ideally run in background, but we can run synchronously for MVP verification
    result = service.ingest_synthetic_dataset(base_dir, case_id)
    return {"message": "Synthetic data ingested", "results": result}

@router.get("/cases/{case_id}/ingestion-summary", summary="Get summary of ingestion jobs")
def get_ingestion_summary(case_id: str, db: Session = Depends(get_db)):
    """Retrieve summary of all processing jobs for a case."""
    jobs = db.query(ProcessingJob).filter_by(case_id=case_id).all()
    return {
        "case_id": case_id,
        "total_jobs": len(jobs),
        "jobs": [
            {
                "job_id": job.id,
                "type": job.job_type,
                "status": job.status,
                "total_rows": job.total_rows,
                "processed_rows": job.processed_rows,
                "rejected_rows": job.rejected_rows
            } for job in jobs
        ]
    }

@router.post("/documents/{document_id}/process", summary="Process a specific document")
def process_document(document_id: str, db: Session = Depends(get_db)):
    """Trigger processing (NLP or CSV parsing) on an uploaded document."""
    return {"message": f"Processing triggered for {document_id}"}

@router.get("/documents/{document_id}/processing-status", summary="Get document processing status")
def get_processing_status(document_id: str, db: Session = Depends(get_db)):
    """Get the status of a document processing job."""
    job = db.query(ProcessingJob).filter_by(document_id=document_id).order_by(ProcessingJob.created_at.desc()).first()
    if not job:
        raise HTTPException(status_code=404, detail="No processing job found for this document.")
    return {"job_id": job.id, "status": job.status, "errors": job.error_summary}

@router.post("/graph/sync/retry", summary="Retry failed graph syncs")
def retry_graph_sync(case_id: str, service: IngestionService = Depends(get_ingestion_service)):
    """Retry graph synchronization for records marked RETRYABLE_FAILURE."""
    # Mock implementation for milestone
    return {"message": "Retry initiated.", "case_id": case_id}

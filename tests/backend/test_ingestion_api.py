"""Tests for ingestion API endpoints."""

import pytest
from unittest.mock import patch
from apps.backend.app.models.processing_job import ProcessingJob

def test_upload_invalid_file_extension(admin_client):
    with open(__file__, 'rb') as f:
        # Pass a .py file, which should be rejected
        response = admin_client.post(
            "/api/v1/cases/C001/upload",
            files={"file": ("test_ingestion_api.py", f, "text/x-python")}
        )
    assert "CSV and JSON" in response.json().get("detail", "")
    # I'll just check 400.

def test_upload_invalid_file_extension_2(admin_client):
    with open(__file__, 'rb') as f:
        response = admin_client.post(
            "/api/v1/cases/C001/upload",
            files={"file": ("test_ingestion_api.py", f, "text/x-python")}
        )
    assert response.status_code == 400
    detail = response.json().get("detail") or response.json().get("error", {}).get("message", "")
    assert "CSV and JSON" in detail

@patch("os.path.exists")
@patch("apps.backend.app.ingestion.service.IngestionService.ingest_synthetic_dataset")
def test_ingest_synthetic_endpoint(mock_ingest, mock_exists, admin_client):
    mock_ingest.return_value = {"people": {"processed_rows": 10}}
    mock_exists.return_value = True
    
    # Needs synthetic files to exist in data/synthetic, which they do because of our earlier step
    response = admin_client.post("/api/v1/cases/C001/ingest-synthetic")
    assert response.status_code == 200
    assert "Synthetic data ingested" in response.json()["message"]

def test_get_ingestion_summary(admin_client, db_session):
    # Setup mock job
    job = ProcessingJob(case_id="C001", job_type="TEST", status="COMPLETED", total_rows=5)
    db_session.add(job)
    db_session.commit()
    
    response = admin_client.get("/api/v1/cases/C001/ingestion-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_jobs"] >= 1
    assert data["jobs"][-1]["status"] == "COMPLETED"
    assert data["jobs"][-1]["total_rows"] == 5

def test_process_document(admin_client):
    response = admin_client.post("/api/v1/documents/doc1/process")
    assert response.status_code == 200

def test_retry_graph_sync(admin_client):
    response = admin_client.post("/api/v1/graph/sync/retry?case_id=C001")
    assert response.status_code == 200

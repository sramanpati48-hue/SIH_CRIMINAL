"""Tests for the ingestion orchestration service."""

import os
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from apps.backend.app.ingestion.service import IngestionService, GraphServiceUnavailableError
from apps.backend.app.models.processing_job import ProcessingJob
from apps.backend.app.models.entity import ExtractedEntity

@pytest.fixture
def mock_csv_file(tmp_path):
    csv_file = tmp_path / "people.csv"
    csv_file.write_text("case_id,person_id,name,alias,dob\nC001,P001,John Doe,JD,1980-01-01\nC002,P002,Jane Doe,,1990-01-01\n", encoding="utf-8")
    return str(csv_file)


def test_ingest_people_success(db_session: Session, mock_csv_file):
    # Mock Neo4j driver as available
    with patch("apps.backend.app.graph.driver.neo4j_manager.is_available", return_value=True):
        with patch("apps.backend.app.graph.repository.GraphRepository.create_or_merge_entity") as mock_repo:
            service = IngestionService(db_session)
            
            result = service.ingest_people(mock_csv_file, "C001")
            
            assert result.total_rows == 2
            assert result.processed_rows == 2
            assert result.rejected_rows == 0
            assert result.neo4j_status == "SYNCED"
            assert result.retryable_record_count == 0
            
            # Check Postgres
            entities = db_session.query(ExtractedEntity).filter_by(source_record_type="Person").all()
            assert len(entities) == 2
            assert entities[0].canonical_name == "John Doe"
            assert entities[0].graph_sync_status == "SYNCED"
            
            # Check Neo4j mock calls
            assert mock_repo.call_count == 2
            
            # Check Job
            job = db_session.query(ProcessingJob).filter_by(id=result.processing_job_id).first()
            assert job.status == "COMPLETED"
            assert job.processed_rows == 2


def test_ingest_people_neo4j_offline(db_session: Session, mock_csv_file):
    # Mock Neo4j driver as unavailable
    with patch("apps.backend.app.graph.driver.neo4j_manager.is_available", return_value=False):
        service = IngestionService(db_session)
        
        # Clear entities table from previous test just in case (test isolation should handle this, but let's be safe if shared session)
        db_session.query(ExtractedEntity).delete()
        db_session.commit()
        
        result = service.ingest_people(mock_csv_file, "C001")
        
        assert result.processed_rows == 2
        assert result.neo4j_status == "OFFLINE/FAILED"
        assert result.retryable_record_count == 2
        
        # Postgres data MUST still be saved
        entities = db_session.query(ExtractedEntity).filter_by(source_record_type="Person").all()
        assert len(entities) == 2
        assert entities[0].graph_sync_status == "RETRYABLE_FAILURE"
        
        job = db_session.query(ProcessingJob).filter_by(id=result.processing_job_id).first()
        assert job.status == "COMPLETED_WITH_ERRORS"


def test_ingestion_idempotency(db_session: Session, mock_csv_file):
    with patch("apps.backend.app.graph.driver.neo4j_manager.is_available", return_value=True):
        with patch("apps.backend.app.graph.repository.GraphRepository.create_or_merge_entity"):
            service = IngestionService(db_session)
            
            db_session.query(ExtractedEntity).delete()
            db_session.commit()
            
            # Run first time
            res1 = service.ingest_people(mock_csv_file, "C001")
            assert res1.processed_rows == 2
            
            # Run second time on same file
            res2 = service.ingest_people(mock_csv_file, "C001")
            assert res2.processed_rows == 2
            
            # Ensure no duplicates in Postgres
            entities = db_session.query(ExtractedEntity).filter_by(source_record_type="Person").all()
            assert len(entities) == 2 # Still exactly 2

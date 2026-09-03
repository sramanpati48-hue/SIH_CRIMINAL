"""Tests for the memory-conscious CSV reader."""

import os
import pytest
from apps.backend.app.ingestion.csv_reader import stream_csv_file, IngestionRowError
from apps.backend.app.ingestion.schemas import PersonRecord

def test_csv_reader_valid_and_invalid_rows(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("case_id,person_id,name,alias,dob\nC001,P001,John Doe,JD,1980-01-01\nC001,P002,,,\nC001,P003,Jane Doe,,\n", encoding="utf-8")
    
    results = list(stream_csv_file(str(csv_file), PersonRecord))
    
    # 3 rows total
    assert len(results) == 3
    
    # Row 1 (valid)
    assert results[0][0] == 2 # row number 2 (header is 1)
    assert results[0][1].name == "John Doe"
    assert len(results[0][2]) == 0
    
    # Row 2 (invalid, name empty)
    assert results[1][0] == 3
    assert results[1][1] is None
    assert len(results[1][2]) > 0
    assert isinstance(results[1][2][0], IngestionRowError)
    assert "name" in results[1][2][0].field_name
    
    # Row 3 (valid)
    assert results[2][1].name == "Jane Doe"

def test_csv_reader_empty_file(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("", encoding="utf-8")
    
    results = list(stream_csv_file(str(csv_file), PersonRecord))
    assert len(results) == 1
    assert results[0][1] is None
    assert "empty" in results[0][2][0].message

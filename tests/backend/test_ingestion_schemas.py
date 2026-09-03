"""Tests for Pydantic ingestion schemas."""

import pytest
from pydantic import ValidationError
from apps.backend.app.ingestion.schemas import PersonRecord, TransactionRecord

def test_valid_person_record():
    p = PersonRecord(case_id="C001", person_id="P001", name="John Doe")
    assert p.case_id == "C001"
    assert p.name == "John Doe"

def test_invalid_person_record_empty_name():
    with pytest.raises(ValidationError):
        PersonRecord(case_id="C001", person_id="P001", name="   ")

def test_invalid_person_record_extra_field():
    with pytest.raises(ValidationError):
        PersonRecord(case_id="C001", person_id="P001", name="John Doe", extra_hacker_field="123")

def test_valid_transaction_record():
    tx = TransactionRecord(
        case_id="C001", transaction_id="TX001", source_account="A1", target_account="A2", 
        amount=100.5, timestamp="2026-09-02T10:00:00"
    )
    assert tx.amount == 100.5

def test_invalid_transaction_amount():
    with pytest.raises(ValidationError):
        TransactionRecord(
            case_id="C001", transaction_id="TX001", source_account="A1", target_account="A2", 
            amount=-50.0, timestamp="2026-09-02T10:00:00"
        )
    with pytest.raises(ValidationError):
        TransactionRecord(
            case_id="C001", transaction_id="TX001", source_account="A1", target_account="A2", 
            amount=0.0, timestamp="2026-09-02T10:00:00"
        )

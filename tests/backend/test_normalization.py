"""Tests for pure normalization functions."""

from datetime import datetime
from apps.backend.app.ingestion.normalization import (
    normalize_string, normalize_name, normalize_phone, 
    normalize_vehicle_id, normalize_account_id, normalize_date, normalize_amount
)

def test_normalize_string():
    assert normalize_string("  hello \n world ") == "hello world"
    assert normalize_string(None) == ""
    assert normalize_string(123) == "123"

def test_normalize_name():
    assert normalize_name("  JOHN   doe ") == "John Doe"

def test_normalize_phone():
    assert normalize_phone("+1 555-0100") == "+15550100"
    assert normalize_phone("555-0100") == "+5550100"
    assert normalize_phone("0555") == "0555" # Starts with 0, don't prepend + naively

def test_normalize_vehicle_id():
    assert normalize_vehicle_id("abc 123-xyz") == "ABC123XYZ"

def test_normalize_account_id():
    assert normalize_account_id(" ba001 ") == "BA001"

def test_normalize_date():
    dt = normalize_date("2026-09-02T15:30:00")
    assert isinstance(dt, datetime)
    assert dt.year == 2026
    
    dt2 = normalize_date("2026-09-02T15:30:00Z")
    assert dt2.year == 2026
    
    assert normalize_date("invalid") is None

def test_normalize_amount():
    assert normalize_amount("100.50") == 100.5
    assert normalize_amount("invalid") is None

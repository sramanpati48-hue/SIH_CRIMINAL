"""Tests for synthetic data generation and determinism."""

import os
import csv
import json
import pytest

from data.synthetic.generate_data import generate, OUTPUT_DIR

def test_synthetic_data_generation_creates_files():
    generate()
    
    assert os.path.exists(os.path.join(OUTPUT_DIR, "cases.csv"))
    assert os.path.exists(os.path.join(OUTPUT_DIR, "people.csv"))
    assert os.path.exists(os.path.join(OUTPUT_DIR, "phones.csv"))
    assert os.path.exists(os.path.join(OUTPUT_DIR, "vehicles.csv"))
    assert os.path.exists(os.path.join(OUTPUT_DIR, "locations.csv"))
    assert os.path.exists(os.path.join(OUTPUT_DIR, "calls.csv"))
    assert os.path.exists(os.path.join(OUTPUT_DIR, "transactions.csv"))
    assert os.path.exists(os.path.join(OUTPUT_DIR, "case_reports.json"))

def test_planted_pattern_cross_case_connector():
    with open(os.path.join(OUTPUT_DIR, "people.csv"), 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        p001 = [p for p in reader if p["person_id"] == "P001"][0]
        cases = p001["case_id"].split(",")
        assert len(cases) == 3
        assert cases == ["C001", "C002", "C003"]

def test_planted_pattern_shared_phone():
    with open(os.path.join(OUTPUT_DIR, "phones.csv"), 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        ph001 = [p for p in reader if p["phone_id"] == "PH001"][0]
        owners = ph001["owner_person_id"].split(",")
        assert len(owners) == 2
        assert "P002" in owners
        assert "P003" in owners

def test_planted_pattern_rapid_transaction_chain():
    with open(os.path.join(OUTPUT_DIR, "transactions.csv"), 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        chain = [t for t in reader if t["transaction_id"].startswith("TX_CHAIN_")]
        assert len(chain) == 3
        assert chain[0]["source_account"] == "BA001"
        assert chain[0]["target_account"] == "BA002"
        assert chain[1]["source_account"] == "BA002"
        assert chain[1]["target_account"] == "BA003"

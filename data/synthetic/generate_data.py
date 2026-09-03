"""Synthetic data generator for SIH 26189 Prototype."""

import csv
import json
import os
import random
from datetime import datetime, timedelta
from faker import Faker

# Seed for deterministic generation
SEED = 42
fake = Faker()
fake.seed_instance(SEED)
random.seed(SEED)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def generate():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Cases (10)
    cases = []
    for i in range(1, 11):
        case_id = f"C{i:03d}"
        cases.append({
            "case_id": case_id,
            "title": f"Operation {fake.word().capitalize()}",
            "status": "OPEN",
            "opened_at": fake.date_time_this_year().isoformat()
        })
        
    # 2. People (30+)
    people = []
    # Generate 35 people to leave room for specific patterns
    for i in range(1, 36):
        people.append({
            "person_id": f"P{i:03d}",
            "name": fake.name(),
            "alias": fake.first_name() if random.random() > 0.5 else "",
            "dob": fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
            "case_id": random.choice(cases)["case_id"]
        })
        
    # Pattern 1: Cross-case connector (P001 is in C001, C002, C003)
    p001 = people[0]
    p001["case_id"] = "C001,C002,C003" # Storing multiple as a comma-separated string for ingestion to parse
    
    # Pattern 6: Bridge relationship (P010 connects Case 4 cluster to Case 5 cluster)
    p010 = people[9]
    p010["case_id"] = "C004,C005"
    
    # Pattern 7: Legitimate high-connectivity example (Bank)
    # We will model this as an Organization, but for simplicity, let's just make it a well-known org in transactions
    
    # 3. Phones (20)
    phones = []
    for i in range(1, 21):
        phones.append({
            "phone_id": f"PH{i:03d}",
            "number": f"+1-555-{random.randint(1000, 9999)}",
            "owner_person_id": random.choice(people)["person_id"],
            "case_id": random.choice(cases)["case_id"]
        })
        
    # Pattern 2: Shared phone (PH001 used by P002 and P003)
    phones[0]["owner_person_id"] = "P002,P003"
    
    # 4. Vehicles (15)
    vehicles = []
    for i in range(1, 16):
        vehicles.append({
            "vehicle_id": f"V{i:03d}",
            "plate": fake.license_plate(),
            "owner_person_id": random.choice(people)["person_id"],
            "case_id": random.choice(cases)["case_id"]
        })
        
    # Pattern 3: Shared vehicle (V001 in C006, C007)
    vehicles[0]["case_id"] = "C006,C007"
    
    # 5. Locations (15)
    locations = []
    for i in range(1, 16):
        locations.append({
            "location_id": f"LOC{i:03d}",
            "address": fake.address().replace("\n", ", "),
            "case_id": random.choice(cases)["case_id"]
        })
        
    # 6. Calls (100)
    calls = []
    base_time = datetime.now() - timedelta(days=30)
    for i in range(1, 101):
        caller = random.choice(phones)
        receiver = random.choice([p for p in phones if p["phone_id"] != caller["phone_id"]])
        call_time = base_time + timedelta(hours=random.randint(1, 700))
        calls.append({
            "caller_phone_id": caller["phone_id"],
            "receiver_phone_id": receiver["phone_id"],
            "timestamp": call_time.isoformat(),
            "duration_seconds": random.randint(10, 3600),
            "case_id": caller["case_id"].split(",")[0]
        })
        
    # 7. Transactions (75)
    transactions = []
    for i in range(1, 76):
        tx_time = base_time + timedelta(hours=random.randint(1, 700))
        transactions.append({
            "transaction_id": f"TX{i:03d}",
            "source_account": f"BA{random.randint(1, 20):03d}",
            "target_account": f"BA{random.randint(1, 20):03d}",
            "amount": round(random.uniform(10.0, 10000.0), 2),
            "timestamp": tx_time.isoformat(),
            "case_id": random.choice(cases)["case_id"]
        })
        
    # Pattern 5: Rapid transaction chain (BA001 -> BA002 -> BA003 within 48 hours)
    chain_time = base_time + timedelta(days=10)
    transactions[0] = {
        "transaction_id": "TX_CHAIN_1",
        "source_account": "BA001",
        "target_account": "BA002",
        "amount": 5000.00,
        "timestamp": chain_time.isoformat(),
        "case_id": "C001"
    }
    transactions[1] = {
        "transaction_id": "TX_CHAIN_2",
        "source_account": "BA002",
        "target_account": "BA003",
        "amount": 4900.00,
        "timestamp": (chain_time + timedelta(hours=2)).isoformat(),
        "case_id": "C001"
    }
    transactions[2] = {
        "transaction_id": "TX_CHAIN_3",
        "source_account": "BA003",
        "target_account": "BA004",
        "amount": 4800.00,
        "timestamp": (chain_time + timedelta(hours=26)).isoformat(), # Within 48 hours
        "case_id": "C001"
    }

    # Legitimate high-connectivity: BA050 is a 'Central Bank Hub' which does many transactions
    for i in range(3, 13):
        transactions[i]["source_account"] = "BA050"
        
    # Pattern 4: Repeated location (P004, P005, P006 all at LOC002 around same time)
    # We will embed this in Case Reports for NLP or direct extraction if location-events are ingested
    
    # 8. Case Reports (10)
    case_reports = []
    for i in range(1, 11):
        case_reports.append({
            "report_id": f"DOC{i:03d}",
            "case_id": f"C{i:03d}",
            "text": f"Surveillance report for case C{i:03d}. Suspects were observed."
        })
        
    # Inject repeated location text into C002 report
    case_reports[1]["text"] = "On " + (base_time + timedelta(days=5)).strftime("%Y-%m-%d") + " at approximately 14:00, individuals P004, P005, and P006 were all observed holding a meeting at location LOC002."

    # Write CSVs
    def write_csv(filename, fieldnames, data):
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    write_csv("cases.csv", ["case_id", "title", "status", "opened_at"], cases)
    write_csv("people.csv", ["person_id", "name", "alias", "dob", "case_id"], people)
    write_csv("phones.csv", ["phone_id", "number", "owner_person_id", "case_id"], phones)
    write_csv("vehicles.csv", ["vehicle_id", "plate", "owner_person_id", "case_id"], vehicles)
    write_csv("locations.csv", ["location_id", "address", "case_id"], locations)
    write_csv("calls.csv", ["caller_phone_id", "receiver_phone_id", "timestamp", "duration_seconds", "case_id"], calls)
    write_csv("transactions.csv", ["transaction_id", "source_account", "target_account", "amount", "timestamp", "case_id"], transactions)

    # Write JSON
    with open(os.path.join(OUTPUT_DIR, "case_reports.json"), "w", encoding="utf-8") as f:
        json.dump(case_reports, f, indent=2)

    print("Synthetic data generated successfully.")

if __name__ == "__main__":
    generate()

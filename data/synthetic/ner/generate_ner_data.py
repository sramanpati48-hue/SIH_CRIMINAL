"""Deterministic Synthetic NER and Relationship Evaluation Dataset Generator.

Generates reproducible, synthetic, annotated documents for Named Entity
Recognition (NER) and Relationship Extraction (RE) evaluation.

Core Rules:
1. Purely synthetic data: uses strictly fictitious phone numbers (+1-555-01xx),
   fictitious bank accounts (SYN-BA-xxxx), fictitious case IDs (CASE-xxxx-SYN),
   fictitious vehicles (SYN-xxx), and synthetic person/organization names.
2. Character offset preservation: text[start:end] == entity_text is verified.
3. Document-level split separation: train, validation, and test splits have
   disjoint document IDs and distinct template scenario families.
4. Includes negative examples (zero entities/relationships), ambiguous decoys,
   spelling variations, aliases, and malformed OCR artifacts.
"""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple


ENTITY_LABELS = {
    "PERSON",
    "ALIAS",
    "PHONE",
    "VEHICLE",
    "LOCATION",
    "ORGANIZATION",
    "BANK_ACCOUNT",
    "CASE_ID",
    "DATE",
    "MONEY",
}

RELATIONSHIP_LABELS = {
    "CALLED",
    "USED",
    "OWNS",
    "VISITED",
    "TRANSFERRED_TO",
    "INVOLVED_IN",
    "MENTIONED_IN",
    "CONNECTED_TO",
    "OCCURRED_AT",
}


@dataclass
class DocumentBuilder:
    """Helper to incrementally build text while recording exact entity and relationship spans."""
    document_id: str
    split: str
    scenario_type: str
    text_chunks: List[str] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    current_offset: int = 0
    entity_idx: int = 0
    rel_idx: int = 0

    def add_text(self, text: str) -> DocumentBuilder:
        self.text_chunks.append(text)
        self.current_offset += len(text)
        return self

    def add_entity(self, text: str, label: str) -> str:
        if label not in ENTITY_LABELS:
            raise ValueError(f"Invalid entity label: {label}")
        start = self.current_offset
        end = start + len(text)
        ent_id = f"{self.document_id}_e{self.entity_idx}"
        self.entity_idx += 1

        self.entities.append({
            "id": ent_id,
            "label": label,
            "start": start,
            "end": end,
            "text": text,
        })
        self.text_chunks.append(text)
        self.current_offset = end
        return ent_id

    def add_relationship(
        self,
        rel_type: str,
        source_id: str,
        target_id: str,
        evidence_text: str = "",
    ) -> str:
        if rel_type not in RELATIONSHIP_LABELS:
            raise ValueError(f"Invalid relationship label: {rel_type}")
        rel_id = f"{self.document_id}_r{self.rel_idx}"
        self.rel_idx += 1

        self.relationships.append({
            "id": rel_id,
            "type": rel_type,
            "source_entity_id": source_id,
            "target_entity_id": target_id,
            "text": evidence_text,
        })
        return rel_id

    def build(self) -> Dict[str, Any]:
        full_text = "".join(self.text_chunks)
        # Verify strict character slice integrity
        for ent in self.entities:
            slice_text = full_text[ent["start"]:ent["end"]]
            if slice_text != ent["text"]:
                raise AssertionError(
                    f"Offset mismatch in {self.document_id} for {ent['id']}: "
                    f"expected {ent['text']!r}, found {slice_text!r} at [{ent['start']}:{ent['end']}]"
                )
        return {
            "document_id": self.document_id,
            "split": self.split,
            "scenario_type": self.scenario_type,
            "text": full_text,
            "entities": self.entities,
            "relationships": self.relationships,
        }


# Seeded deterministic value pools for variety and spelling variations
FIRST_NAMES = [
    "Marcus", "Marcuz", "Elena", "Helena", "Tariq", "Tareq", "Julian", "Julien",
    "Catharina", "Katarina", "Viktor", "Victor", "Devon", "Jonathon", "Johnathan",
    "Siddharth", "Sidney", "Alina", "Dmitri", "Dmitry", "Nadia", "Nadya", "Lucas"
]
LAST_NAMES = [
    "Vance", "Smythe", "Smith", "Al-Mansoor", "Mansoor", "Kowalski", "Petrov",
    "Moretti", "O'Connor", "Chen", "Van Der Bilt", "Morales", "Sterling", "Kovacs"
]
ALIASES = [
    "The Ghost", "Nightowl", "Apex", "Cipher", "Shorty", "Red Fox", "Specter",
    "Razor", "Silver Fox", "Blackbird", "The Broker", "Viper", "Echo"
]
COMPANIES = [
    "Apex Logistics Fictitious Corp", "Synthetic Holdings Ltd", "First Fictional Credit Union",
    "Omega Shell Trading Co", "Atlas Cargo Services Inc", "Pinnacle Horizon Imports LLC",
    "Northwind Clandestine Freight", "Zenith Synthetic Maritime Ltd", "Biscayne Bay Trade Co"
]
LOCATIONS = [
    "Warehouse 4, 100 Industrial Parkway, Sector 9",
    "Pier 42, North Harbor, Docklands",
    "Suite 300, 500 Fictional Blvd, Central City",
    "Room 104, Synthetic Motel, Highway 7",
    "Safehouse Charlie at 848 Meadow Lane, Greenview",
    "Terminal 2 Cargo Bay, East Port Facility",
    "Basement Office, 12 Old Brick Road, Oldtown",
    "Berth 17, South Anchorage Port, Bay City",
    "Sublevel Parking 3B, Metro Tower Plaza",
    "Depot 9, Rail Cargo Yard, District 4"
]
DECOY_TEXTS = [
    "General maintenance was performed during the routine morning inspection.",
    "Officers gave chase across the open field before losing visual contact.",
    "The team expressed hope that progress would accelerate in the coming months.",
    "In late March, seasonal temperature swings disrupted logistical schedules.",
    "The bill for fuel supply and fleet repair was settled through standard administrative channels.",
    "A major security audit of the facility perimeters was concluded without notable incident.",
    "Liberty and procedural fairness were preserved during the interview sequence.",
    "Thermal readings from the cooling units indicated steady baseline performance.",
    "The vehicle mentioned in the anonymous rumor could not be independently corroborated.",
    "An unknown individual called someone on an unregistered device with zero identifying metadata."
]


def _phone(rng: random.Random) -> str:
    # Strictly in the 555-0100 to 555-0199 fictitious range
    suffix = rng.randint(100, 199)
    fmt = rng.choice(["+1-555-0{suffix}", "(555) 0{suffix}", "555-0{suffix}", "+15550{suffix}"])
    return fmt.format(suffix=suffix)


def _bank_acct(rng: random.Random) -> str:
    num = rng.randint(10000, 99999)
    prefix = rng.choice(["SYN-BA-", "ACC-SYN-", "SYN-ACCT-", "BA-SYN-"])
    return f"{prefix}{num}"


def _vehicle(rng: random.Random) -> str:
    num = rng.randint(1000, 9999)
    pfx = rng.choice(["SYN-VEH-", "SYN-TRK-", "SYN-VAN-", "SYN-SED-", "SYN-SUV-"])
    return f"{pfx}{num}"


def _money(rng: random.Random) -> str:
    amt = rng.choice([4500, 12000, 25000, 48500, 75000, 120000, 350000])
    fmt = rng.choice(["${:,}", "${:,.2f}", "USD {:,}", "{:,} dollars"])
    if fmt == "{:,} dollars":
        return fmt.format(amt)
    return fmt.format(amt)


def _date(rng: random.Random) -> str:
    year = rng.choice([2023, 2024])
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    fmt = rng.choice(["iso", "word", "slash", "dash_word"])
    months_words = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    months_full = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    if fmt == "iso":
        return f"{year:04d}-{month:02d}-{day:02d}"
    elif fmt == "word":
        return f"{months_full[month - 1]} {day}, {year}"
    elif fmt == "slash":
        return f"{day:02d}/{month:02d}/{year}"
    else:
        return f"{day:02d}-{months_words[month - 1]}-{year}"


# ============================================================================
# TRAIN SPLIT GENERATION (Templates T1 - T8)
# ============================================================================

def generate_train_documents(rng: random.Random) -> List[Dict[str, Any]]:
    docs = []

    for i in range(1, 41):
        doc_id = f"DOC_TR_{i:03d}"
        t_type = i % 8

        if t_type == 1:
            # T1: Financial Wire Fraud & Shell Entity Layering
            # Entities: PERSON, ALIAS, BANK_ACCOUNT (x2), MONEY, DATE, CASE_ID, ORGANIZATION
            # Rel: TRANSFERRED_TO, OWNS, INVOLVED_IN
            b = DocumentBuilder(doc_id, "train", "financial_wire_layering")
            person = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            alias = rng.choice(ALIASES)
            ba1 = _bank_acct(rng)
            ba2 = _bank_acct(rng)
            amount = _money(rng)
            date_str = _date(rng)
            case_id = f"CASE-2024-SYN-{100 + i}"
            org = rng.choice(COMPANIES)

            b.add_text(f"Financial crimes investigator intake memorandum for case ")
            cid_e = b.add_entity(case_id, "CASE_ID")
            b.add_text(". On ")
            d_e = b.add_entity(date_str, "DATE")
            b.add_text(", primary subject ")
            p_e = b.add_entity(person, "PERSON")
            b.add_text(" (operating under the street alias '")
            a_e = b.add_entity(alias, "ALIAS")
            b.add_text(f"') authorized an electronic funds wire. Acting as a controlling director of ")
            o_e = b.add_entity(org, "ORGANIZATION")
            b.add_text(", the subject ordered a transfer of ")
            m_e = b.add_entity(amount, "MONEY")
            b.add_text(" from primary escrow account ")
            ba1_e = b.add_entity(ba1, "BANK_ACCOUNT")
            b.add_text(" directly to correspondent account ")
            ba2_e = b.add_entity(ba2, "BANK_ACCOUNT")
            b.add_text(". Both the individual and the corporate entity are formally investigated under ")
            b.add_text(f"active proceedings.")

            b.add_relationship("OWNS", p_e, ba1_e, f"{person} owns {ba1}")
            b.add_relationship("TRANSFERRED_TO", ba1_e, ba2_e, f"transferred {amount} from {ba1} to {ba2}")
            b.add_relationship("INVOLVED_IN", p_e, cid_e, f"{person} involved in {case_id}")
            b.add_relationship("INVOLVED_IN", o_e, cid_e, f"{org} involved in {case_id}")
            b.add_relationship("USED", p_e, a_e, f"{person} used alias {alias}")
            docs.append(b.build())

        elif t_type == 2:
            # T2: Field Surveillance & Safehouse Meeting
            # Entities: PERSON (x2), LOCATION, DATE, CASE_ID, VEHICLE
            # Rel: VISITED, OCCURRED_AT, CONNECTED_TO
            b = DocumentBuilder(doc_id, "train", "field_surveillance_meeting")
            p1 = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            p2 = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            loc = rng.choice(LOCATIONS)
            date_str = _date(rng)
            case_id = f"CASE-2024-SYN-{150 + i}"
            veh = _vehicle(rng)

            b.add_text("PHYSICAL SURVEILLANCE LOG: File ")
            c_e = b.add_entity(case_id, "CASE_ID")
            b.add_text(". Date of surveillance: ")
            d_e = b.add_entity(date_str, "DATE")
            b.add_text(". At 19:45 hours, operative unit Alpha observed ")
            p1_e = b.add_entity(p1, "PERSON")
            b.add_text(" arriving at ")
            l_e = b.add_entity(loc, "LOCATION")
            b.add_text(". The subject arrived operating a motor vehicle bearing registration ")
            v_e = b.add_entity(veh, "VEHICLE")
            b.add_text(". Approximately twenty minutes later, associate ")
            p2_e = b.add_entity(p2, "PERSON")
            b.add_text(" entered the facility on foot. Visual confirmation was established through window blinds.")

            b.add_relationship("VISITED", p1_e, l_e, f"{p1} arrived at {loc}")
            b.add_relationship("VISITED", p2_e, l_e, f"{p2} entered {loc}")
            b.add_relationship("USED", p1_e, v_e, f"{p1} operating vehicle {veh}")
            b.add_relationship("CONNECTED_TO", p1_e, p2_e, f"{p1} met with associate {p2}")
            b.add_relationship("OCCURRED_AT", c_e, l_e, f"surveillance occurred at {loc}")
            docs.append(b.build())

        elif t_type == 3:
            # T3: Traffic Stop & Registered Vehicle Search
            # Entities: PERSON, VEHICLE, LOCATION, DATE, CASE_ID, PHONE
            # Rel: OWNS, USED, OCCURRED_AT, INVOLVED_IN
            b = DocumentBuilder(doc_id, "train", "traffic_interdiction")
            driver = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            veh = _vehicle(rng)
            loc = rng.choice(LOCATIONS)
            date_str = _date(rng)
            case_id = f"CASE-2024-SYN-{200 + i}"
            phone = _phone(rng)

            b.add_text("INCIDENT REPORT: Registered Case ")
            c_e = b.add_entity(case_id, "CASE_ID")
            b.add_text(". On ")
            d_e = b.add_entity(date_str, "DATE")
            b.add_text(", highway patrol conducted an evidentiary stop at ")
            l_e = b.add_entity(loc, "LOCATION")
            b.add_text(". The vehicle was identified as a commercial transport unit with registration plate ")
            v_e = b.add_entity(veh, "VEHICLE")
            b.add_text(". The registered owner and sole occupant was identified as ")
            p_e = b.add_entity(driver, "PERSON")
            b.add_text(". During inventory inspection, officers recovered an encrypted telecommunications handset with subscriber number ")
            ph_e = b.add_entity(phone, "PHONE")
            b.add_text(". The operator admitted possession and regular use of the handset.")

            b.add_relationship("OWNS", p_e, v_e, f"{driver} registered owner of {veh}")
            b.add_relationship("USED", p_e, ph_e, f"{driver} admitted regular use of {phone}")
            b.add_relationship("OCCURRED_AT", c_e, l_e, f"incident occurred at {loc}")
            b.add_relationship("INVOLVED_IN", p_e, c_e, f"{driver} involved in {case_id}")
            docs.append(b.build())

        elif t_type == 4:
            # T4: Telecommunications Intercept Log
            # Entities: PERSON (x2), PHONE (x2), DATE, CASE_ID
            # Rel: CALLED, USED, MENTIONED_IN
            b = DocumentBuilder(doc_id, "train", "telecom_intercept")
            caller = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            callee = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            ph1 = _phone(rng)
            ph2 = _phone(rng)
            date_str = _date(rng)
            case_id = f"CASE-2024-SYN-{250 + i}"

            b.add_text("LINE INTERCEPT TRANSCRIPTION SUMMARY for Judicial Dossier ")
            c_e = b.add_entity(case_id, "CASE_ID")
            b.add_text(". Session timestamp: ")
            d_e = b.add_entity(date_str, "DATE")
            b.add_text(". Originating line ")
            ph1_e = b.add_entity(ph1, "PHONE")
            b.add_text(", subscribed to subject ")
            p1_e = b.add_entity(caller, "PERSON")
            b.add_text(", initiated an outbound communication to target line ")
            ph2_e = b.add_entity(ph2, "PHONE")
            b.add_text(", verified to be in possession of ")
            p2_e = b.add_entity(callee, "PERSON")
            b.add_text(". Call duration recorded was 240 seconds. Both parties discussed ongoing matters related to the inquiry.")

            b.add_relationship("CALLED", ph1_e, ph2_e, f"{ph1} called {ph2}")
            b.add_relationship("USED", p1_e, ph1_e, f"{caller} used line {ph1}")
            b.add_relationship("USED", p2_e, ph2_e, f"{callee} used line {ph2}")
            b.add_relationship("MENTIONED_IN", p1_e, c_e, f"{caller} mentioned in {case_id}")
            b.add_relationship("MENTIONED_IN", p2_e, c_e, f"{callee} mentioned in {case_id}")
            docs.append(b.build())

        elif t_type == 5:
            # T5: Search Warrant Evidence Inventory
            # Entities: PERSON, ORGANIZATION, BANK_ACCOUNT, MONEY, CASE_ID, LOCATION
            # Rel: CONNECTED_TO, INVOLVED_IN, OCCURRED_AT, OWNS
            b = DocumentBuilder(doc_id, "train", "warrant_inventory")
            custodian = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            org = rng.choice(COMPANIES)
            ba = _bank_acct(rng)
            cash = _money(rng)
            case_id = f"CASE-2024-SYN-{300 + i}"
            loc = rng.choice(LOCATIONS)

            b.add_text("WARRANT EXECUTION RETURN: Case Reference ")
            c_e = b.add_entity(case_id, "CASE_ID")
            b.add_text(". Premises searched: ")
            l_e = b.add_entity(loc, "LOCATION")
            b.add_text(". On-site manager ")
            p_e = b.add_entity(custodian, "PERSON")
            b.add_text(" was present during execution on behalf of ")
            o_e = b.add_entity(org, "ORGANIZATION")
            b.add_text(". In the executive safe, investigators inventoried liquid currency totaling ")
            m_e = b.add_entity(cash, "MONEY")
            b.add_text(", alongside corporate bank statements identifying treasury ledger ")
            ba_e = b.add_entity(ba, "BANK_ACCOUNT")
            b.add_text(". The records were secured into evidence.")

            b.add_relationship("CONNECTED_TO", p_e, o_e, f"{custodian} connected to {org}")
            b.add_relationship("OWNS", o_e, ba_e, f"{org} owns {ba}")
            b.add_relationship("OCCURRED_AT", c_e, l_e, f"search occurred at {loc}")
            b.add_relationship("INVOLVED_IN", p_e, c_e, f"{custodian} involved in {case_id}")
            docs.append(b.build())

        elif t_type == 6:
            # T6: Negative Control (Zero entities and zero relationships)
            b = DocumentBuilder(doc_id, "train", "negative_control_routine_admin")
            sample_decoy = rng.choice(DECOY_TEXTS)
            b.add_text(
                f"ROUTINE FACILITY SUPERVISION REPORT. Shift supervisor completed environmental log checks. "
                f"{sample_decoy} "
                f"All access doors remained electronically locked throughout the duty cycle. "
                f"No unusual occurrences or unauthorized personnel ingress observed."
            )
            docs.append(b.build())

        elif t_type == 7:
            # T7: Decoy & Ambiguity Narrative (words like March, Bill, General as decoys, with 1-2 real entities)
            b = DocumentBuilder(doc_id, "train", "ambiguous_decoy_narrative")
            real_person = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            case_id = f"CASE-2024-SYN-{350 + i}"
            phone = _phone(rng)

            b.add_text(f"INVESTIGATIVE BRIEFING for Case ")
            c_e = b.add_entity(case_id, "CASE_ID")
            b.add_text(". The field team noted that general surveillance was conducted in late March near the springs. ")
            b.add_text("Officers maintained hope while following up on an unpaid bill. Amid these routine checks, target ")
            p_e = b.add_entity(real_person, "PERSON")
            b.add_text(" was observed utilizing telephone terminal ")
            ph_e = b.add_entity(phone, "PHONE")
            b.add_text(". A major review is scheduled for the upcoming session.")

            b.add_relationship("USED", p_e, ph_e, f"{real_person} used {phone}")
            b.add_relationship("MENTIONED_IN", p_e, c_e, f"{real_person} mentioned in {case_id}")
            docs.append(b.build())

        else:
            # T8: Malformed Punctuation & OCR Artifacts (Testing boundary robustness)
            b = DocumentBuilder(doc_id, "train", "malformed_ocr_formatting")
            name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            case_id = f"CASE-2024-SYN-{400 + i}"
            veh = _vehicle(rng)
            ba = _bank_acct(rng)
            cash = _money(rng)

            b.add_text(f"RAW-SCAN-MEMO: Case[")
            c_e = b.add_entity(case_id, "CASE_ID")
            b.add_text(f"];TargetSubject: ")
            p_e = b.add_entity(name, "PERSON")
            b.add_text(f" ;VehicleID:(")
            v_e = b.add_entity(veh, "VEHICLE")
            b.add_text(f"). BankWireDetails: deposited ")
            m_e = b.add_entity(cash, "MONEY")
            b.add_text(f" into account ")
            ba_e = b.add_entity(ba, "BANK_ACCOUNT")
            b.add_text(f"; verification pending review.")

            b.add_relationship("OWNS", p_e, v_e, f"{name} owns {veh}")
            b.add_relationship("INVOLVED_IN", p_e, c_e, f"{name} involved in {case_id}")
            docs.append(b.build())

    return docs


# ============================================================================
# VALIDATION SPLIT GENERATION (Templates V1 - V5, Distinct Scenarios)
# ============================================================================

def generate_validation_documents(rng: random.Random) -> List[Dict[str, Any]]:
    docs = []

    for i in range(1, 16):
        doc_id = f"DOC_VAL_{i:03d}"
        v_type = i % 5

        if v_type == 1:
            # V1: Maritime Cargo & Smuggling Manifest Investigation
            # Entities: ORGANIZATION, PERSON, LOCATION, DATE, CASE_ID, VEHICLE
            # Rel: VISITED, CONNECTED_TO, INVOLVED_IN, OWNS
            b = DocumentBuilder(doc_id, "validation", "maritime_cargo_tracking")
            org = rng.choice(COMPANIES)
            inspector = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            loc = rng.choice(LOCATIONS)
            date_str = _date(rng)
            case_id = f"CASE-VAL-SYN-{500 + i}"
            vessel = _vehicle(rng)

            b.add_text("PORT AUTHORITY SPECIAL AUDIT: File ")
            c_e = b.add_entity(case_id, "CASE_ID")
            b.add_text(". Date filed: ")
            d_e = b.add_entity(date_str, "DATE")
            b.add_text(". Maritime logistics firm ")
            o_e = b.add_entity(org, "ORGANIZATION")
            b.add_text(" chartered cargo hauler ")
            v_e = b.add_entity(vessel, "VEHICLE")
            b.add_text(" which berthed at ")
            l_e = b.add_entity(loc, "LOCATION")
            b.add_text(". Custom clearing agent ")
            p_e = b.add_entity(inspector, "PERSON")
            b.add_text(" submitted declaration manifests on behalf of the shipping syndicate.")

            b.add_relationship("OWNS", o_e, v_e, f"{org} chartered {vessel}")
            b.add_relationship("VISITED", v_e, l_e, f"{vessel} berthed at {loc}")
            b.add_relationship("CONNECTED_TO", p_e, o_e, f"{inspector} connected to {org}")
            b.add_relationship("INVOLVED_IN", o_e, c_e, f"{org} involved in {case_id}")
            docs.append(b.build())

        elif v_type == 2:
            # V2: Burner Device Chain & Clandestine Handshake
            # Entities: PERSON (x2), ALIAS, PHONE (x2), LOCATION, DATE
            # Rel: CALLED, USED, VISITED, OCCURRED_AT
            b = DocumentBuilder(doc_id, "validation", "burner_device_chain")
            agent = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            handler = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            alias = rng.choice(ALIASES)
            ph1 = _phone(rng)
            ph2 = _phone(rng)
            loc = rng.choice(LOCATIONS)
            date_str = _date(rng)

            b.add_text("COMMUNICATIONS INTERCEPT MEMO. Date: ")
            d_e = b.add_entity(date_str, "DATE")
            b.add_text(". Subject ")
            p1_e = b.add_entity(agent, "PERSON")
            b.add_text(" (code name '")
            a_e = b.add_entity(alias, "ALIAS")
            b.add_text("') dialed from disposable line ")
            ph1_e = b.add_entity(ph1, "PHONE")
            b.add_text(" to incoming device ")
            ph2_e = b.add_entity(ph2, "PHONE")
            b.add_text(" held by ")
            p2_e = b.add_entity(handler, "PERSON")
            b.add_text(". The two later scheduled an in-person meeting at ")
            l_e = b.add_entity(loc, "LOCATION")
            b.add_text(" to exchange documents.")

            b.add_relationship("USED", p1_e, a_e, f"{agent} used alias {alias}")
            b.add_relationship("USED", p1_e, ph1_e, f"{agent} used {ph1}")
            b.add_relationship("CALLED", ph1_e, ph2_e, f"{ph1} called {ph2}")
            b.add_relationship("VISITED", p1_e, l_e, f"{agent} visited {loc}")
            b.add_relationship("OCCURRED_AT", ph1_e, l_e, f"meeting agreed at {loc}")
            docs.append(b.build())

        elif v_type == 3:
            # V3: Bank Compliance Suspicious Activity Report (SAR)
            # Entities: BANK_ACCOUNT (x2), MONEY, ORGANIZATION, DATE, CASE_ID
            # Rel: TRANSFERRED_TO, OWNS, MENTIONED_IN
            b = DocumentBuilder(doc_id, "validation", "bank_compliance_sar")
            ba1 = _bank_acct(rng)
            ba2 = _bank_acct(rng)
            amount = _money(rng)
            org = rng.choice(COMPANIES)
            date_str = _date(rng)
            case_id = f"CASE-VAL-SYN-{550 + i}"

            b.add_text("FINANCIAL COMPLIANCE SAR: Registered case ")
            c_e = b.add_entity(case_id, "CASE_ID")
            b.add_text(". Date of audit: ")
            d_e = b.add_entity(date_str, "DATE")
            b.add_text(". An alert flagged customer account ")
            ba1_e = b.add_entity(ba1, "BANK_ACCOUNT")
            b.add_text(" registered to ")
            o_e = b.add_entity(org, "ORGANIZATION")
            b.add_text(". The ledger records an automated wire of ")
            m_e = b.add_entity(amount, "MONEY")
            b.add_text(" directed toward offshore beneficiary ledger ")
            ba2_e = b.add_entity(ba2, "BANK_ACCOUNT")
            b.add_text(". Internal compliance marked the transaction for human verification.")

            b.add_relationship("OWNS", o_e, ba1_e, f"{org} owns {ba1}")
            b.add_relationship("TRANSFERRED_TO", ba1_e, ba2_e, f"wire of {amount} from {ba1} to {ba2}")
            b.add_relationship("MENTIONED_IN", ba1_e, c_e, f"{ba1} mentioned in {case_id}")
            docs.append(b.build())

        elif v_type == 4:
            # V4: Negative Control (Zero entities and zero relationships)
            b = DocumentBuilder(doc_id, "validation", "negative_control_fleet_audit")
            b.add_text(
                "ANNUAL MOTOR POOL EQUIPMENT AND DIAGNOSTICS LOG. Routine maintenance scheduled for vehicles. "
                "Staff conducted oil changes and tire pressure certifications. "
                "No incident reports, unauthorized deployments, or operational irregularities recorded during the reporting quarter."
            )
            docs.append(b.build())

        else:
            # V5: High-Density Multi-Alias Debrief with Spelling Variations
            b = DocumentBuilder(doc_id, "validation", "multi_alias_debrief")
            name_var = rng.choice(["Jonathon Smythe", "Catharina Van Der Bilt", "Marcuz Kovacs", "Tareq Al-Mansoor"])
            alias = rng.choice(ALIASES)
            phone = _phone(rng)
            veh = _vehicle(rng)
            case_id = f"CASE-VAL-SYN-{600 + i}"

            b.add_text(f"INTELLIGENCE DEBRIEF: Cross-case dossier ")
            c_e = b.add_entity(case_id, "CASE_ID")
            b.add_text(f". Informant confirmed that operative ")
            p_e = b.add_entity(name_var, "PERSON")
            b.add_text(f", also recognized across intercepted chats as '")
            a_e = b.add_entity(alias, "ALIAS")
            b.add_text(f"', operates utility vehicle ")
            v_e = b.add_entity(veh, "VEHICLE")
            b.add_text(f" and routes inquiries through contact point ")
            ph_e = b.add_entity(phone, "PHONE")
            b.add_text(f". All intelligence requires corroboration.")

            b.add_relationship("USED", p_e, a_e, f"{name_var} used alias {alias}")
            b.add_relationship("OWNS", p_e, v_e, f"{name_var} owns {veh}")
            b.add_relationship("USED", p_e, ph_e, f"{name_var} used {phone}")
            b.add_relationship("MENTIONED_IN", p_e, c_e, f"{name_var} mentioned in {case_id}")
            docs.append(b.build())

    return docs


# ============================================================================
# TEST SPLIT GENERATION (Templates S1 - S5, Multi-Party Adversarial Scenarios)
# ============================================================================

def generate_test_documents(rng: random.Random) -> List[Dict[str, Any]]:
    docs = []

    for i in range(1, 21):
        doc_id = f"DOC_TEST_{i:03d}"
        s_type = i % 5

        if s_type == 1:
            # S1: Triangulated Multi-Jurisdiction Syndicate Meeting
            # Entities: PERSON (x2), ALIAS, ORGANIZATION, LOCATION, DATE, CASE_ID, VEHICLE
            # Rel: VISITED, CONNECTED_TO, OCCURRED_AT, INVOLVED_IN
            b = DocumentBuilder(doc_id, "test", "triangulated_syndicate_meet")
            p1 = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            p2 = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            alias = rng.choice(ALIASES)
            org = rng.choice(COMPANIES)
            loc = rng.choice(LOCATIONS)
            date_str = _date(rng)
            case_id = f"CASE-TEST-SYN-{700 + i}"
            veh = _vehicle(rng)

            b.add_text("JOINT TASK FORCE SITUATION REPORT: Case ")
            c_e = b.add_entity(case_id, "CASE_ID")
            b.add_text(". Date of observation: ")
            d_e = b.add_entity(date_str, "DATE")
            b.add_text(". Surveillance assets deployed around ")
            l_e = b.add_entity(loc, "LOCATION")
            b.add_text(". At 21:10 hours, ")
            p1_e = b.add_entity(p1, "PERSON")
            b.add_text(" (monitored under street alias '")
            a_e = b.add_entity(alias, "ALIAS")
            b.add_text("') arrived in transport unit ")
            v_e = b.add_entity(veh, "VEHICLE")
            b.add_text(". The subject met with counterpart ")
            p2_e = b.add_entity(p2, "PERSON")
            b.add_text(", who represents commercial entity ")
            o_e = b.add_entity(org, "ORGANIZATION")
            b.add_text(". Investigators documented mutual coordination between both actors.")

            b.add_relationship("VISITED", p1_e, l_e, f"{p1} visited {loc}")
            b.add_relationship("USED", p1_e, v_e, f"{p1} used {veh}")
            b.add_relationship("CONNECTED_TO", p1_e, p2_e, f"{p1} connected to {p2}")
            b.add_relationship("CONNECTED_TO", p2_e, o_e, f"{p2} connected to {org}")
            b.add_relationship("OCCURRED_AT", c_e, l_e, f"incident occurred at {loc}")
            b.add_relationship("INVOLVED_IN", p1_e, c_e, f"{p1} involved in {case_id}")
            docs.append(b.build())

        elif s_type == 2:
            # S2: Smurfing & Micro-Structuring Chain Across Multiple Accounts
            # Entities: PERSON, BANK_ACCOUNT (x2), MONEY (x2), DATE, ORGANIZATION
            # Rel: TRANSFERRED_TO, OWNS, CONNECTED_TO
            b = DocumentBuilder(doc_id, "test", "financial_micro_structuring")
            courier = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            org = rng.choice(COMPANIES)
            ba1 = _bank_acct(rng)
            ba2 = _bank_acct(rng)
            m1 = _money(rng)
            m2 = _money(rng)
            date_str = _date(rng)

            b.add_text("FINANCIAL INTELLIGENCE AUDIT LOG. Event date: ")
            d_e = b.add_entity(date_str, "DATE")
            b.add_text(". Subject ")
            p_e = b.add_entity(courier, "PERSON")
            b.add_text(" acting on instructions from entity ")
            o_e = b.add_entity(org, "ORGANIZATION")
            b.add_text(" conducted split remittances. First, an initial deposit of ")
            m1_e = b.add_entity(m1, "MONEY")
            b.add_text(" was routed to ledger ")
            ba1_e = b.add_entity(ba1, "BANK_ACCOUNT")
            b.add_text(". Immediately following, a secondary transfer of ")
            m2_e = b.add_entity(m2, "MONEY")
            b.add_text(" was dispatched from that ledger into secondary account ")
            ba2_e = b.add_entity(ba2, "BANK_ACCOUNT")
            b.add_text(". The pattern suggests intentional threshold avoidance.")

            b.add_relationship("CONNECTED_TO", p_e, o_e, f"{courier} connected to {org}")
            b.add_relationship("OWNS", p_e, ba1_e, f"{courier} owns {ba1}")
            b.add_relationship("TRANSFERRED_TO", ba1_e, ba2_e, f"transferred funds from {ba1} to {ba2}")
            docs.append(b.build())

        elif s_type == 3:
            # S3: Cold Case Historical File Review with Telecom Tracking
            # Entities: PERSON, PHONE (x2), CASE_ID (x2), DATE
            # Rel: CALLED, USED, MENTIONED_IN, INVOLVED_IN
            b = DocumentBuilder(doc_id, "test", "historical_case_linkage")
            suspect = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            ph1 = _phone(rng)
            ph2 = _phone(rng)
            cid1 = f"CASE-HIST-SYN-{800 + i}"
            cid2 = f"CASE-CURRENT-SYN-{850 + i}"
            date_str = _date(rng)

            b.add_text("HISTORICAL INVESTIGATIVE REVIEW linking cold case dossier ")
            c1_e = b.add_entity(cid1, "CASE_ID")
            b.add_text(" with active investigation ")
            c2_e = b.add_entity(cid2, "CASE_ID")
            b.add_text(". Historical archives indicate that on ")
            d_e = b.add_entity(date_str, "DATE")
            b.add_text(", person of interest ")
            p_e = b.add_entity(suspect, "PERSON")
            b.add_text(" operated telephone station ")
            ph1_e = b.add_entity(ph1, "PHONE")
            b.add_text(". Telecom logs verify that this line called counterpart handset ")
            ph2_e = b.add_entity(ph2, "PHONE")
            b.add_text(", establishing cross-case operational overlap.")

            b.add_relationship("USED", p_e, ph1_e, f"{suspect} used {ph1}")
            b.add_relationship("CALLED", ph1_e, ph2_e, f"{ph1} called {ph2}")
            b.add_relationship("INVOLVED_IN", p_e, c1_e, f"{suspect} involved in {cid1}")
            b.add_relationship("MENTIONED_IN", p_e, c2_e, f"{suspect} mentioned in {cid2}")
            docs.append(b.build())

        elif s_type == 4:
            # S4: Negative Control (Pure baseline text, no entities)
            b = DocumentBuilder(doc_id, "test", "negative_control_datacenter_access")
            b.add_text(
                "INFORMATION TECHNOLOGY SERVER ROOM ACCESS AUDIT. Environmental air handlers operated within specifications. "
                "Badge access readers completed standard cryptographic heartbeat handshakes. "
                "No hardware faults, access exceptions, or unauthorized physical intrusions occurred during this audit window."
            )
            docs.append(b.build())

        else:
            # S5: Adversarial OCR & Noisy Decoy Surveillance Log
            b = DocumentBuilder(doc_id, "test", "adversarial_ocr_noisy")
            name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            alias = rng.choice(ALIASES)
            loc = rng.choice(LOCATIONS)
            phone = _phone(rng)
            case_id = f"CASE-TEST-SYN-{900 + i}"

            b.add_text(f"SPECIAL OPS SCAN:FileRef[")
            c_e = b.add_entity(case_id, "CASE_ID")
            b.add_text(f"]. During late March field checks, officers had high hope for resolution. ")
            b.add_text(f"General maintenance units observed subject ")
            p_e = b.add_entity(name, "PERSON")
            b.add_text(f" (alias: '")
            a_e = b.add_entity(alias, "ALIAS")
            b.add_text(f"') entering premises at ")
            l_e = b.add_entity(loc, "LOCATION")
            b.add_text(f". The subject then transmitted SMS alerts via terminal ")
            ph_e = b.add_entity(phone, "PHONE")
            b.add_text(f". Disregard false decoys regarding Bill and Major.")

            b.add_relationship("USED", p_e, a_e, f"{name} used alias {alias}")
            b.add_relationship("VISITED", p_e, l_e, f"{name} visited {loc}")
            b.add_relationship("USED", p_e, ph_e, f"{name} used {phone}")
            b.add_relationship("OCCURRED_AT", c_e, l_e, f"event occurred at {loc}")
            docs.append(b.build())

    return docs


# ============================================================================
# MAIN DATASET GENERATION WORKFLOW
# ============================================================================

def generate_dataset(
    seed: int = 26189,
    output_dir: str | Path | None = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Generate deterministic train, validation, and test NER/RE datasets."""
    rng = random.Random(seed)

    train_docs = generate_train_documents(rng)
    val_docs = generate_validation_documents(rng)
    test_docs = generate_test_documents(rng)

    # Validate split separation
    train_ids = {d["document_id"] for d in train_docs}
    val_ids = {d["document_id"] for d in val_docs}
    test_ids = {d["document_id"] for d in test_docs}

    if not train_ids.isdisjoint(val_ids):
        raise AssertionError(f"Leakage between train and validation: {train_ids & val_ids}")
    if not train_ids.isdisjoint(test_ids):
        raise AssertionError(f"Leakage between train and test: {train_ids & test_ids}")
    if not val_ids.isdisjoint(test_ids):
        raise AssertionError(f"Leakage between validation and test: {val_ids & test_ids}")

    if output_dir is not None:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        def write_jsonl(filename: str, docs: List[Dict[str, Any]]):
            file_path = out_path / filename
            with open(file_path, "w", encoding="utf-8") as f:
                for doc in docs:
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")

        write_jsonl("train.jsonl", train_docs)
        write_jsonl("validation.jsonl", val_docs)
        write_jsonl("test.jsonl", test_docs)

    return train_docs, val_docs, test_docs


if __name__ == "__main__":
    target_dir = Path(__file__).resolve().parent
    train_docs, val_docs, test_docs = generate_dataset(seed=26189, output_dir=target_dir)
    print(f"Successfully generated deterministic dataset in {target_dir}:")
    print(f"  - train.jsonl:      {len(train_docs)} documents")
    print(f"  - validation.jsonl: {len(val_docs)} documents")
    print(f"  - test.jsonl:       {len(test_docs)} documents")

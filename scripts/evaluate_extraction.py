import argparse
import json
import sys
import os
from datetime import datetime, timezone

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.backend.app.evaluation.provider_comparison import compare_providers

def load_jsonl(filepath):
    data = []
    if not os.path.exists(filepath):
        return data
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def main():
    parser = argparse.ArgumentParser(description="Evaluate NER Providers on Synthetic Test Data")
    parser.add_argument("--provider", nargs='+', default=["MOCK"], help="List of providers to evaluate (e.g., MOCK SPACY_LOCAL)")
    parser.add_argument("--dataset", default="data/synthetic/ner/test.jsonl", help="Path to synthetic test dataset")
    parser.add_argument("--output-dir", default="apps/backend/reports", help="Directory to save evaluation reports")
    args = parser.parse_args()

    print(f"Loading synthetic dataset from {args.dataset}...")
    documents = load_jsonl(args.dataset)
    if not documents:
        print(f"Error: Could not load dataset {args.dataset}")
        sys.exit(1)
        
    gold_entities = []
    gold_relationships = []
    
    for doc in documents:
        doc_id = doc.get("id", doc.get("document_id"))
        for ent in doc.get("entities", []):
            ent["document_id"] = doc_id
            gold_entities.append(ent)
        for rel in doc.get("relationships", []):
            rel["document_id"] = doc_id
            gold_relationships.append(rel)
            
    print(f"Loaded {len(documents)} documents, {len(gold_entities)} gold entities, {len(gold_relationships)} gold relationships.")
    print(f"Evaluating providers: {', '.join(args.provider)}...")
    
    result = compare_providers(
        providers=args.provider,
        documents=documents,
        gold_entities=gold_entities,
        gold_relationships=gold_relationships,
        dataset_version="v1.0-synthetic"
    )
    
    # Print concise metrics
    for p in result.providers:
        print(f"\n--- Provider: {p.provider} ({p.provider_status}) ---")
        if p.provider_status != "AVAILABLE":
            for w in p.warnings:
                print(f"  Warning: {w}")
            continue
            
        print("  Entity Metrics:")
        print(f"    Precision: {p.entity_metrics.precision:.4f}")
        print(f"    Recall:    {p.entity_metrics.recall:.4f}")
        print(f"    F1 Score:  {p.entity_metrics.f1:.4f}")
        
        print("  Relationship Metrics:")
        print(f"    Precision: {p.relationship_metrics.exact_relationship_precision:.4f}")
        print(f"    Recall:    {p.relationship_metrics.exact_relationship_recall:.4f}")
        print(f"    F1 Score:  {p.relationship_metrics.exact_relationship_f1:.4f}")

    # Ensure output dir exists within project
    out_dir = os.path.abspath(args.output_dir)
    if not out_dir.startswith(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))):
        print("Error: --output-dir must be within the project root.")
        sys.exit(1)
        
    os.makedirs(out_dir, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(out_dir, f"evaluation_{timestamp}.json")
    md_path = os.path.join(out_dir, f"evaluation_{timestamp}.md")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(result.model_dump_json(indent=2))
        
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Extraction Evaluation Report\n\n")
        f.write(f"**Date**: {result.evaluation_timestamp}\n")
        f.write(f"**Dataset**: {result.dataset_version}\n\n")
        for p in result.providers:
            f.write(f"## {p.provider} ({p.provider_status})\n")
            if p.provider_status == "AVAILABLE":
                f.write(f"- Provider Version: {p.provider_version}\n")
                f.write(f"- Model Version: {p.model_version}\n")
                f.write(f"- Extraction Version: {p.extraction_version}\n")
                
                f.write(f"\n### Entities\n")
                f.write(f"- F1: {p.entity_metrics.f1:.4f}\n")
                f.write(f"- Precision: {p.entity_metrics.precision:.4f}\n")
                f.write(f"- Recall: {p.entity_metrics.recall:.4f}\n")
                
                f.write(f"\n### Relationships\n")
                f.write(f"- F1: {p.relationship_metrics.exact_relationship_f1:.4f}\n")
                f.write(f"- Precision: {p.relationship_metrics.exact_relationship_precision:.4f}\n")
                f.write(f"- Recall: {p.relationship_metrics.exact_relationship_recall:.4f}\n")
            for w in p.warnings:
                f.write(f"\n> **Warning**: {w}\n")
            for l in p.limitations:
                f.write(f"\n> **Limitation**: {l}\n")
            f.write("\n")
            
    print(f"\nReports saved to:\n  - {json_path}\n  - {md_path}")
    
    # Return non-zero only for true FAILED statuses, not UNAVAILABLE.
    if any(p.provider_status == "FAILED" for p in result.providers):
        sys.exit(1)

if __name__ == "__main__":
    main()

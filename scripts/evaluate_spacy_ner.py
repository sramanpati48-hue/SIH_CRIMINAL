import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.backend.app.evaluation.provider_comparison import compare_providers

def main():
    parser = argparse.ArgumentParser(description="Evaluate Trained spaCy NER Model")
    parser.add_argument("--model-id", required=True, help="Model ID to evaluate")
    parser.add_argument("--dataset", default="data/synthetic/ner/test.jsonl", help="Held-out test dataset")
    args = parser.parse_args()
    
    print(f"Evaluating {args.model_id} on {args.dataset}")
    
    from apps.backend.app.db.session import SessionLocal
    from apps.backend.app.models.extraction_model import ExtractionModel
    import json
    
    db = SessionLocal()
    try:
        model_reg = db.query(ExtractionModel).filter(ExtractionModel.model_id == args.model_id).first()
        if not model_reg:
            print(f"Model ID {args.model_id} not found in database.")
            sys.exit(1)
            
        if not model_reg.artifact_path or not os.path.exists(model_reg.artifact_path):
            print(f"Artifact path {model_reg.artifact_path} does not exist.")
            sys.exit(1)
            
        print(f"Found model at {model_reg.artifact_path}")
        
        # Load dataset
        documents = []
        gold_entities = []
        gold_relationships = []
        with open(args.dataset, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                doc = json.loads(line)
                documents.append(doc)
                doc_id = doc.get("id", doc.get("document_id"))
                for ent in doc.get("entities", []):
                    ent["document_id"] = doc_id
                    gold_entities.append(ent)
                for rel in doc.get("relationships", []):
                    rel["document_id"] = doc_id
                    gold_relationships.append(rel)
                    
        # Update get_provider_instance logic locally for comparison
        from apps.backend.app.evaluation.provider_comparison import compare_providers, get_provider_instance
        # We need to monkeypatch get_provider_instance to pass the model_path, but compare_providers 
        # doesn't pass model_path yet.
        # Let's write a small wrapper here for now.
        from apps.backend.app.extraction.local_ner_provider import SpacyNERProvider
        from apps.backend.app.extraction.relationship_service import RelationshipExtractionService
        from apps.backend.app.evaluation.entity_metrics import evaluate_entities
        from apps.backend.app.evaluation.relationship_metrics import evaluate_relationships
        
        extractor = SpacyNERProvider(model_name=model_reg.artifact_path, provider_name="SPACY_CUSTOM")
        extractor._check_availability()
        
        pred_entities_flat = []
        pred_relationships_flat = []
        rel_svc = RelationshipExtractionService(None, extractor.provider_name, extractor.extraction_version)
        
        for doc in documents:
            doc_id = doc.get("id", doc.get("document_id"))
            text = doc.get("text", doc.get("content", ""))
            res = extractor.extract(doc_id, text)
            pred_entities_flat.extend([e.model_dump() for e in res.entities])
            rel_cands = rel_svc.extract_relationships(doc_id, "N/A", text, res.entities)
            pred_relationships_flat.extend([r.model_dump() for r in rel_cands])
            
        ent_metrics = evaluate_entities(gold_entities, pred_entities_flat)
        rel_metrics = evaluate_relationships(gold_relationships, pred_relationships_flat, gold_entities, pred_entities_flat)
        
        # Save metrics to DB
        model_reg.test_metrics = {
            "entity_f1": ent_metrics.f1,
            "entity_precision": ent_metrics.precision,
            "entity_recall": ent_metrics.recall,
            "relationship_f1": rel_metrics.exact_relationship_f1
        }
        db.commit()
        
        print("\n=== Evaluation Results ===")
        print(f"Entity F1: {ent_metrics.f1:.4f} (P: {ent_metrics.precision:.4f}, R: {ent_metrics.recall:.4f})")
        print(f"Relationship F1: {rel_metrics.exact_relationship_f1:.4f}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()

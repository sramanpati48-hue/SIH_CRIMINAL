import argparse
import sys
import os
import json

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.backend.app.training.readiness import check_training_readiness
from apps.backend.app.training.spacy_data import convert_to_spacy_format

def main():
    parser = argparse.ArgumentParser(description="Prepare spaCy NER training data")
    parser.add_argument("--data-dir", default="data/synthetic/ner", help="Input directory")
    parser.add_argument("--output-dir", default="data/training/spacy", help="Output directory")
    parser.add_argument("--force", action="store_true", help="Force generation even if not ready")
    args = parser.parse_args()
    
    status = check_training_readiness(data_dir=args.data_dir)
    if status.status == "NOT_READY" and not args.force:
        print("Training readiness checks failed. Please fix errors before generating training data.")
        sys.exit(1)
        
    os.makedirs(args.output_dir, exist_ok=True)
    
    splits = ["train", "validation", "test"]
    
    summary = {}
    for split in splits:
        input_path = os.path.join(args.data_dir, f"{split}.jsonl")
        if not os.path.exists(input_path):
            print(f"Skipping {split}, file not found: {input_path}")
            continue
            
        output_path = os.path.join(args.output_dir, f"{split}.spacy")
        print(f"Converting {input_path} -> {output_path}...")
        
        res = convert_to_spacy_format(input_path, output_path)
        summary[split] = res
        
        print(f"  Docs: {res['document_count']}")
        print(f"  Entities: {res['entity_count']} (Skipped: {res['skipped_entities']})")
        
    with open(os.path.join(args.output_dir, "conversion_metadata.json"), "w") as f:
        json.dump(summary, f, indent=2)
        
    print("\nConversion complete.")

if __name__ == "__main__":
    main()

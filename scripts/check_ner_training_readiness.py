import argparse
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.backend.app.training.readiness import check_training_readiness

def main():
    parser = argparse.ArgumentParser(description="Check NER Training Readiness")
    parser.add_argument("--data-dir", default="data/synthetic/ner", help="Directory containing synthetic datasets")
    args = parser.parse_args()

    print(f"Checking training readiness using data directory: {args.data_dir}\n")
    
    status = check_training_readiness(data_dir=args.data_dir)
    
    print(f"=== Readiness Status: {status.status} ===\n")
    print(f"Dataset Version: {status.dataset_version}")
    print(f"Training Enabled: {status.training_enabled}\n")
    
    def print_split(name, split):
        if not split.exists:
            print(f"{name}: MISSING")
            return
        print(f"{name}:")
        print(f"  Documents: {split.document_count}")
        print(f"  Entities:  {split.entity_count}")
        print(f"  Labels:")
        for l in split.label_distribution:
            suff = "OK" if l.is_sufficient else "INSUFFICIENT"
            print(f"    - {l.label}: {l.count} ({suff})")
            
    print_split("Train Split", status.train_split)
    print()
    print_split("Validation Split", status.validation_split)
    print()
    print_split("Test Split", status.test_split)
    print()
    
    if status.warnings:
        print("=== WARNINGS ===")
        for w in status.warnings:
            print(f" - {w}")
        print()
            
    if status.errors:
        print("=== ERRORS ===")
        for e in status.errors:
            print(f" - {e}")
        print()
        
    if status.status == "NOT_READY":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()

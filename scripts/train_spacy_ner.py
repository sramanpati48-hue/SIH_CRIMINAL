import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.backend.app.training.readiness import check_training_readiness
from apps.backend.app.training.spacy_train import train_spacy_model
from apps.backend.app.db.session import SessionLocal
from apps.backend.app.models.extraction_model import ExtractionModel

def main():
    parser = argparse.ArgumentParser(description="Train spaCy NER Model")
    parser.add_argument("--data-dir", default="data/training/spacy", help="Prepared spaCy data dir")
    parser.add_argument("--force", action="store_true", help="Bypass readiness checks")
    args = parser.parse_args()
    
    status = check_training_readiness()
    if status.status == "NOT_READY" and not args.force:
        print("Training readiness checks failed. Aborting training.")
        sys.exit(1)
        
    train_path = os.path.join(args.data_dir, "train.spacy")
    val_path = os.path.join(args.data_dir, "validation.spacy")
    
    if not os.path.exists(train_path) or not os.path.exists(val_path):
        print(f"Prepared data not found in {args.data_dir}. Run prepare_spacy_ner_data.py first.")
        sys.exit(1)
        
    print("Starting spaCy training...")
    try:
        metadata = train_spacy_model(
            train_data_path=train_path,
            val_data_path=val_path,
        )
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)
    
    # Register in DB
    db = SessionLocal()
    try:
        model_reg = ExtractionModel(
            model_id=metadata["model_id"],
            provider=metadata["provider"],
            model_type=metadata["model_type"],
            model_version=metadata["model_version"],
            dataset_version=metadata["dataset_version"],
            extraction_version=metadata["extraction_version"],
            label_schema_version=metadata["label_schema_version"],
            artifact_storage_key=metadata["artifact_storage_key"],
            artifact_filename=metadata["artifact_filename"],
            sha256_checksum=metadata["sha256_checksum"],
            spacy_version=metadata["spacy_version"],
            python_version=metadata["python_version"],
            status=metadata["status"]
        )
        db.add(model_reg)
        db.commit()
        print(f"Model successfully trained and registered: {metadata['model_id']}")
    except Exception as e:
        print(f"Failed to register model in DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

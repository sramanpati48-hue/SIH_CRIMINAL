import os
import sys
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from apps.backend.app.db.session import SessionLocal
from apps.backend.app.models.user import User, Role
from apps.backend.app.models.case import Case
from apps.backend.app.models.entity import ExtractedEntity
from apps.backend.app.models.relationship import ExtractedRelationship
from apps.backend.app.models.alert import Alert

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def verify_demo_ready():
    warnings = []
    errors = []

    app_env = os.environ.get("APP_ENV", "production").lower()
    if app_env not in ["development", "demo"]:
        errors.append(f"APP_ENV is {app_env}. Demo scripts require 'development' or 'demo'.")

    try:
        with SessionLocal() as db:
            # Migrations Check
            try:
                db.execute(text("SELECT 1 FROM users LIMIT 1"))
            except Exception as e:
                errors.append("Database migrations are not applied. Run alembic upgrade head.")
                
            # Demo Users
            usernames = ["demo_admin", "demo_investigator", "demo_analyst", "demo_reviewer"]
            users = db.query(User).filter(User.username.in_(usernames)).all()
            if len(users) != 4:
                errors.append(f"Expected 4 demo users, found {len(users)}.")

            # Case
            case = db.query(Case).filter(Case.case_number == "CASE-2024-SYN-001").first()
            if not case:
                errors.append("Demo Case 'CASE-2024-SYN-001' not found.")
            else:
                # Entities and Relationships
                entities = db.query(ExtractedEntity).filter(ExtractedEntity.case_id == case.id).count()
                if entities < 2:
                    errors.append(f"Expected multiple synthetic entities, found {entities}.")
                    
                relationships = db.query(ExtractedRelationship).filter(ExtractedRelationship.case_id == case.id).all()
                if not relationships:
                    errors.append("Expected synthetic relationships, found none.")
                else:
                    has_rejected = any(r.verification_status == "REJECTED" for r in relationships)
                    has_accepted = any(r.verification_status == "ACCEPTED" for r in relationships)
                    if not has_rejected:
                        errors.append("Missing a REJECTED relationship for report exclusion test.")
                    if not has_accepted:
                        errors.append("Missing an ACCEPTED relationship for report inclusion test.")
                
                # Alerts
                alerts = db.query(Alert).filter(Alert.case_id == case.id).count()
                if alerts == 0:
                    errors.append("Missing demo alerts.")
    except Exception as e:
        errors.append(f"PostgreSQL verification failed: {e}")

    # Neo4j check
    try:
        from apps.backend.app.graph.driver import neo4j_manager
        if not neo4j_manager.is_available():
            warnings.append("Neo4j driver unavailable. Graph features will run in fallback mode.")
    except Exception as e:
        warnings.append(f"Neo4j verification raised exception (Offline): {e}")

    # Output
    if warnings:
        logger.warning("\n".join(warnings))
        
    if errors:
        logger.error("\n".join(errors))
        print("NOT_READY")
        sys.exit(1)
        
    if warnings:
        print("READY_WITH_WARNINGS")
        sys.exit(0)
        
    print("READY")
    sys.exit(0)

if __name__ == "__main__":
    verify_demo_ready()

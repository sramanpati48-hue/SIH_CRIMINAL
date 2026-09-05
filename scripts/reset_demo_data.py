import os
import sys
import logging

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from apps.backend.app.db.session import SessionLocal
from apps.backend.app.models.user import User
from apps.backend.app.models.case import Case
from apps.backend.app.models.case_access import CaseAccess
from apps.backend.app.models.document import Document
from apps.backend.app.models.entity import ExtractedEntity
from apps.backend.app.models.relationship import ExtractedRelationship
from apps.backend.app.models.extraction_run import ExtractionRun
from apps.backend.app.models.alert import Alert
from apps.backend.app.models.ml import SimilarityResult, ModelPrediction
from apps.backend.app.models.audit_log import AuditLog
from apps.backend.app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_demo_data():
    app_env = os.environ.get("APP_ENV", "production").lower()
    if app_env not in ["development", "demo"]:
        logger.error(f"Cannot reset demo data. APP_ENV is '{app_env}'. Must be 'development' or 'demo'.")
        sys.exit(1)

    logger.info(f"Starting demo reset in {app_env} environment...")

    from apps.backend.app.db.session import engine
    from apps.backend.app.db.base import Base
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        # Find demo cases (convention: cases created in demo environment or specifically prefixed)
        # For this prototype, all data in demo env is considered synthetic.
        # However, to be safe, we will target specific known demo users and their related data.
        
        # In a real system we'd check for a 'is_synthetic' flag. We will delete cases that start with [DEMO] or were made by demo users.
        demo_usernames = ["demo_admin", "demo_investigator", "demo_analyst", "demo_reviewer"]
        demo_users = db.query(User).filter(User.username.in_(demo_usernames)).all()
        demo_user_ids = [u.id for u in demo_users]
        
        # Get cases associated with demo or explicitly marked
        cases = db.query(Case).filter(
            (Case.created_by.in_(demo_user_ids)) | (Case.title.startswith("[DEMO]"))
        ).all()
        
        case_ids = [c.id for c in cases]
        logger.info(f"Found {len(case_ids)} synthetic demo cases to reset.")

        if case_ids:
            # Delete in order of constraints
            db.query(Alert).filter(Alert.case_id.in_(case_ids)).delete(synchronize_session=False)
            db.query(SimilarityResult).filter(SimilarityResult.current_case_id.in_(case_ids) | SimilarityResult.similar_case_id.in_(case_ids)).delete(synchronize_session=False)
            db.query(ModelPrediction).filter(ModelPrediction.case_id.in_(case_ids)).delete(synchronize_session=False)
            db.query(ExtractionRun).filter(ExtractionRun.case_id.in_(case_ids)).delete(synchronize_session=False)
            db.query(ExtractedRelationship).filter(ExtractedRelationship.case_id.in_(case_ids)).delete(synchronize_session=False)
            db.query(ExtractedEntity).filter(ExtractedEntity.case_id.in_(case_ids)).delete(synchronize_session=False)
            db.query(Document).filter(Document.case_id.in_(case_ids)).delete(synchronize_session=False)
            db.query(CaseAccess).filter(CaseAccess.case_id.in_(case_ids)).delete(synchronize_session=False)
            
            # Clean audit logs for these cases
            db.query(AuditLog).filter(AuditLog.target_id.in_(case_ids)).delete(synchronize_session=False)
            
            # Finally delete the cases
            db.query(Case).filter(Case.id.in_(case_ids)).delete(synchronize_session=False)
            
        # Delete demo users
        if demo_user_ids:
            db.query(User).filter(User.id.in_(demo_user_ids)).delete(synchronize_session=False)
            
        db.commit()
        logger.info("PostgreSQL synthetic demo data reset successful.")
        
    # Neo4j Reset (Independent)
    try:
        from apps.backend.app.graph.driver import neo4j_manager
        if neo4j_manager.is_available():
            with neo4j_manager.get_session() as session:
                # Delete nodes that have a case_id belonging to our synthetic case_ids, or just delete all if in demo env
                if case_ids:
                    session.run("MATCH (n) WHERE n.case_id IN $case_ids DETACH DELETE n", case_ids=case_ids)
                    logger.info("Neo4j synthetic graph data reset successful.")
        else:
            logger.warning("Neo4j driver not available. Skipping graph reset.")
    except Exception as e:
        logger.warning(f"Neo4j reset failed safely (Offline or unavailable): {e}")

if __name__ == "__main__":
    reset_demo_data()

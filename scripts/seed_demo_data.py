import os
import sys
import logging
from sqlalchemy.orm import Session
import uuid

from apps.backend.app.db.session import SessionLocal
from apps.backend.app.models.user import User, Role
from apps.backend.app.models.case import Case
from apps.backend.app.models.case_access import CaseAccess, CaseAccessLevel
from apps.backend.app.models.entity import ExtractedEntity
from apps.backend.app.models.relationship import ExtractedRelationship
from apps.backend.app.models.alert import Alert
from apps.backend.app.models.ml import SimilarityResult, ModelPrediction
from apps.backend.app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_demo_data():
    app_env = os.environ.get("APP_ENV", "production").lower()
    if app_env not in ["development", "demo"]:
        logger.error(f"Cannot seed demo data. APP_ENV is '{app_env}'. Must be 'development' or 'demo'.")
        sys.exit(1)

    logger.info(f"Starting demo seed in {app_env} environment...")
    
    from apps.backend.app.db.session import engine
    from apps.backend.app.db.base import Base
    Base.metadata.create_all(bind=engine)
    
    demo_password = os.environ.get("DEMO_PASSWORD")
    if not demo_password:
        # Request from CLI if not present in env
        logger.info("DEMO_PASSWORD environment variable not set. Please provide a password for the demo users.")
        try:
            demo_password = input("Demo Password: ")
        except EOFError:
            demo_password = "demopassword"
            logger.info("Using fallback demo password (non-interactive).")

    hashed_password = get_password_hash(demo_password)

    with SessionLocal() as db:
        # Users
        users = [
            {"username": "demo_admin", "email": "admin@demo.local", "role": Role.ADMINISTRATOR.value},
            {"username": "demo_investigator", "email": "investigator@demo.local", "role": Role.INVESTIGATOR.value},
            {"username": "demo_analyst", "email": "analyst@demo.local", "role": Role.ANALYST.value},
            {"username": "demo_reviewer", "email": "reviewer@demo.local", "role": Role.REVIEWER.value},
        ]
        
        user_map = {}
        for u in users:
            db_user = db.query(User).filter(User.username == u["username"]).first()
            if not db_user:
                db_user = User(
                    username=u["username"],
                    email=u["email"],
                    password_hash=hashed_password,
                    role=u["role"],
                    is_active=True
                )
                db.add(db_user)
                db.flush()
            user_map[u["role"]] = db_user

        logger.info("Seeded 4 demo users.")

        # Case
        case_num = "CASE-2024-SYN-001"
        case = db.query(Case).filter(Case.case_number == case_num).first()
        if not case:
            case = Case(
                case_number=case_num,
                title="[DEMO] Synthetic Syndicate Operations",
                description="Synthetic case regarding fictional smuggling operations.",
                status="ACTIVE",
                priority="HIGH",
                created_by=user_map[Role.ADMINISTRATOR.value].id
            )
            db.add(case)
            db.flush()

            # Assignments
            # Admin gets global inherently in API, but let's assign explicitly for good measure
            db.add(CaseAccess(user_id=user_map[Role.ADMINISTRATOR.value].id, case_id=case.id, access_level=CaseAccessLevel.MANAGE.value, assigned_by_user_id=user_map[Role.ADMINISTRATOR.value].id))
            db.add(CaseAccess(user_id=user_map[Role.INVESTIGATOR.value].id, case_id=case.id, access_level=CaseAccessLevel.MANAGE.value, assigned_by_user_id=user_map[Role.ADMINISTRATOR.value].id))
            db.add(CaseAccess(user_id=user_map[Role.ANALYST.value].id, case_id=case.id, access_level=CaseAccessLevel.ANALYZE.value, assigned_by_user_id=user_map[Role.ADMINISTRATOR.value].id))
            db.add(CaseAccess(user_id=user_map[Role.REVIEWER.value].id, case_id=case.id, access_level=CaseAccessLevel.REVIEW.value, assigned_by_user_id=user_map[Role.ADMINISTRATOR.value].id))
            db.flush()

        logger.info(f"Seeded demo case {case_num} and access assignments.")

        # Entities
        e_john = ExtractedEntity(case_id=case.id, document_id="doc-1", entity_type="PERSON", original_value="John Doe", canonical_name="John Doe", verification_status="ACCEPTED", confidence_score=0.95)
        e_jane = ExtractedEntity(case_id=case.id, document_id="doc-1", entity_type="PERSON", original_value="Jane Smith", canonical_name="Jane Smith", verification_status="ACCEPTED", confidence_score=0.92)
        e_address = ExtractedEntity(case_id=case.id, document_id="doc-1", entity_type="LOCATION", original_value="123 Fake Street, Springfield", canonical_name="123 Fake Street, Springfield", verification_status="UNREVIEWED", confidence_score=0.88)
        e_phone = ExtractedEntity(case_id=case.id, document_id="doc-1", entity_type="PHONE", original_value="555-0199", canonical_name="555-0199", verification_status="ACCEPTED", confidence_score=0.99)
        e_org = ExtractedEntity(case_id=case.id, document_id="doc-1", entity_type="ORGANIZATION", original_value="Frontway Logistics", canonical_name="Frontway Logistics", verification_status="ACCEPTED", confidence_score=0.85)

        e_u1 = ExtractedEntity(case_id=case.id, document_id="doc-1", entity_type="PERSON", original_value="Mike Johnson", canonical_name="Mike Johnson", verification_status="UNREVIEWED", confidence_score=0.82)
        e_u2 = ExtractedEntity(case_id=case.id, document_id="doc-1", entity_type="VEHICLE", original_value="Black SUV", canonical_name="Black SUV", verification_status="UNREVIEWED", confidence_score=0.78)
        e_u3 = ExtractedEntity(case_id=case.id, document_id="doc-1", entity_type="PHONE", original_value="555-0200", canonical_name="555-0200", verification_status="UNREVIEWED", confidence_score=0.81)
        e_u4 = ExtractedEntity(case_id=case.id, document_id="doc-1", entity_type="LOCATION", original_value="Warehouse 4", canonical_name="Warehouse 4", verification_status="UNREVIEWED", confidence_score=0.89)
        e_u5 = ExtractedEntity(case_id=case.id, document_id="doc-1", entity_type="BANK_ACCOUNT", original_value="ACCT-9988", canonical_name="ACCT-9988", verification_status="UNREVIEWED", confidence_score=0.74)
        
        db.add_all([e_john, e_jane, e_address, e_phone, e_org, e_u1, e_u2, e_u3, e_u4, e_u5])
        db.flush()

        # Relationships
        r1 = ExtractedRelationship(case_id=case.id, document_id="doc-1", source_entity_id=e_john.id, target_entity_id=e_phone.id, relation_type="COMMUNICATED_WITH", verification_status="ACCEPTED", confidence_score=0.91, source_text_snippet="John Doe was seen using phone number 555-0199.")
        r2 = ExtractedRelationship(case_id=case.id, document_id="doc-1", source_entity_id=e_jane.id, target_entity_id=e_org.id, relation_type="OWNS", verification_status="ACCEPTED", confidence_score=0.89, source_text_snippet="Records indicate Jane Smith owns Frontway Logistics.")
        r3 = ExtractedRelationship(case_id=case.id, document_id="doc-1", source_entity_id=e_john.id, target_entity_id=e_address.id, relation_type="RESIDES_AT", verification_status="UNREVIEWED", confidence_score=0.75, source_text_snippet="John Doe might reside at 123 Fake Street, Springfield.")
        # One rejected relationship
        r4 = ExtractedRelationship(case_id=case.id, document_id="doc-1", source_entity_id=e_john.id, target_entity_id=e_jane.id, relation_type="KNOWS", verification_status="REJECTED", confidence_score=0.4, source_text_snippet="A rumor suggested John knows Jane.")
        
        r5 = ExtractedRelationship(case_id=case.id, document_id="doc-1", source_entity_id=e_u1.id, target_entity_id=e_org.id, relation_type="EMPLOYED_BY", verification_status="UNREVIEWED", confidence_score=0.79, source_text_snippet="Mike Johnson works at Frontway Logistics.")
        r6 = ExtractedRelationship(case_id=case.id, document_id="doc-1", source_entity_id=e_u1.id, target_entity_id=e_u2.id, relation_type="DRIVES", verification_status="UNREVIEWED", confidence_score=0.82, source_text_snippet="Mike Johnson was seen driving a Black SUV.")
        r7 = ExtractedRelationship(case_id=case.id, document_id="doc-1", source_entity_id=e_u1.id, target_entity_id=e_u4.id, relation_type="VISITED", verification_status="UNREVIEWED", confidence_score=0.75, source_text_snippet="Mike Johnson frequently visits Warehouse 4.")
        r8 = ExtractedRelationship(case_id=case.id, document_id="doc-1", source_entity_id=e_org.id, target_entity_id=e_u5.id, relation_type="HAS_ACCOUNT", verification_status="UNREVIEWED", confidence_score=0.85, source_text_snippet="Funds were wired to ACCT-9988 belonging to Frontway.")

        db.add_all([r1, r2, r3, r4, r5, r6, r7, r8])
        db.flush()

        # Alerts
        alert = Alert(case_id=case.id, alert_type="PATTERN", severity="HIGH", title="Burner Phone Coordination Pattern", description="Phone 555-0199 contacted by multiple distinct fictional suspects.", status="OPEN")
        db.add(alert)

        # Similarity
        sim = SimilarityResult(
            current_case_id=case.id, 
            similar_case_id=case.id, 
            similarity_score=1.0, 
            explanation="Self-similarity baseline check.", 
            feature_version="v1", 
            analysis_run_id="run-001"
        )
        db.add(sim)

        # Baseline Anomaly ML
        ml_pred = ModelPrediction(
            case_id=case.id, 
            prediction_type="ANOMALY", 
            prediction="ANOMALOUS", 
            score=0.82, 
            explanation="Anomalous sub-graph detected around Frontway Logistics.", 
            model_version="baseline_anomaly_v1", 
            dataset_version="v1", 
            feature_version="v1", 
            analysis_run_id="run-001"
        )
        db.add(ml_pred)

        db.commit()
        logger.info("Demo graph entities, relationships, alerts, and analytics seeded.")

    # Neo4j Graph Sync for Demo
    try:
        from apps.backend.app.graph.driver import neo4j_manager
        if neo4j_manager.is_available():
            # In a real sync we'd call the ingestion logic or graph service
            # For demo seed, if Neo4j is available, we will rely on GraphSyncService if it exists,
            # or just let the user click 'Sync' in the UI.
            logger.info("Neo4j is available. Use the UI to sync the graph, or it will auto-sync on next action.")
        else:
            logger.warning("Neo4j driver not available. Skipping graph sync.")
    except Exception as e:
        logger.warning(f"Neo4j sync failed safely (Offline or unavailable): {e}")

    logger.info("Demo seeding completed successfully.")

if __name__ == "__main__":
    seed_demo_data()

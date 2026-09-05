"""Provider comparison evaluation logic."""
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

from apps.backend.app.extraction.mock_provider import MockExtractor
from apps.backend.app.extraction.local_ner_provider import SpacyNERProvider
from apps.backend.app.extraction.schemas import DocumentExtractionResult, ExtractedEntityCandidate
from apps.backend.app.extraction.relationship_rules import RELATIONSHIP_RULE_VERSION
from apps.backend.app.extraction.relationship_service import RelationshipExtractionService
from apps.backend.app.evaluation.reporting import ProviderComparisonResult, ProviderComparisonItem, ConfidenceDistribution
from apps.backend.app.evaluation.entity_metrics import evaluate_entities
from apps.backend.app.evaluation.relationship_metrics import evaluate_relationships
from apps.backend.app.db.session import SessionLocal

def get_provider_instance(
    provider_name: str,
    model_id: str | None = None,
    db: object | None = None,
) -> "ExtractorProvider | None":
    """Return a provider instance for the given allow-listed provider name.

    Args:
        provider_name: Must be one of MOCK, SPACY_BASELINE, SPACY_CUSTOM.
        model_id: Required when provider_name == SPACY_CUSTOM. Must be a
            registry model_id, never a filesystem path.
        db: Required when provider_name == SPACY_CUSTOM (SQLAlchemy Session).

    Returns None for unrecognised provider names.
    Does NOT silently fall back from SPACY_CUSTOM to MOCK.
    """
    if provider_name in ("MOCK", "MOCK_EXTRACTOR"):
        return MockExtractor()
    elif provider_name in ("SPACY_BASELINE", "SPACY_LOCAL", "SPACY_NER", "LOCAL_NER"):
        return SpacyNERProvider.create_baseline()
    elif provider_name == "SPACY_CUSTOM":
        if not model_id:
            logger.warning(
                "get_provider_instance: SPACY_CUSTOM requested but no model_id supplied."
            )
            return SpacyNERProvider.create_baseline()  # still unavailable but typed
        if db is None:
            raise ValueError("A database session is required to load SPACY_CUSTOM.")
        return SpacyNERProvider.create_custom(model_id, db)
    logger.warning("get_provider_instance: unrecognised provider '%s'.", provider_name)
    return None

def compute_confidence_distribution(entities: List[Any], relationships: List[Any]) -> ConfidenceDistribution:
    low = medium = high = 0
    all_cands = entities + relationships
    for c in all_cands:
        conf = getattr(c, "confidence", 0.0)
        if isinstance(c, dict):
            conf = c.get("confidence", 0.0)
            
        if conf < 0.60:
            low += 1
        elif conf < 0.85:
            medium += 1
        else:
            high += 1
            
    return ConfidenceDistribution(LOW=low, MEDIUM=medium, HIGH=high)


def compare_providers(
    providers: List[str], 
    documents: List[Dict[str, Any]], 
    gold_entities: List[Dict[str, Any]], 
    gold_relationships: List[Dict[str, Any]],
    dataset_version: str
) -> ProviderComparisonResult:
    
    results = []
    evaluation_timestamp = datetime.now(timezone.utc).isoformat()
    test_doc_ids = [doc.get("id", doc.get("document_id")) for doc in documents]
    
    for provider_name in providers:
        extractor = get_provider_instance(provider_name)
        if not extractor:
            results.append(ProviderComparisonItem(
                provider=provider_name,
                provider_status="NOT_INSTALLED",
                provider_version="N/A",
                model_version="N/A",
                extraction_version="N/A",
                post_processing_version="N/A",
                relationship_rule_version="N/A",
                warnings=[f"Provider '{provider_name}' is not supported or not installed."],
                limitations=[]
            ))
            continue
            
        try:
            # Check availability (SpacyNERProvider will raise RuntimeError if missing)
            if hasattr(extractor, "_check_availability"):
                extractor._check_availability()
                
            pred_entities_flat = []
            pred_relationships_flat = []
            
            # Since this is memory-only, we create a dummy session for RelationshipExtractionService just to access rules
            # We won't persist anything
            rel_svc = RelationshipExtractionService(None, extractor.provider_name, extractor.extraction_version)
            
            for doc in documents:
                doc_id = doc.get("id", doc.get("document_id"))
                text = doc.get("text", doc.get("content", ""))
                
                res = extractor.extract(doc_id, text)
                pred_entities_flat.extend([e.model_dump() for e in res.entities])
                
                # Rel extraction
                rel_cands = rel_svc.extract_relationships(doc_id, "N/A", text, res.entities)
                pred_relationships_flat.extend([r.model_dump() for r in rel_cands])
                
            ent_metrics = evaluate_entities(gold_entities, pred_entities_flat)
            rel_metrics = evaluate_relationships(gold_relationships, pred_relationships_flat, gold_entities, pred_entities_flat)
            conf_dist = compute_confidence_distribution(pred_entities_flat, pred_relationships_flat)
            
            results.append(ProviderComparisonItem(
                provider=extractor.provider_name,
                provider_status="AVAILABLE",
                provider_version=extractor.provider_version,
                model_version=extractor.model_version,
                extraction_version=extractor.extraction_version,
                post_processing_version="1.0.0",
                relationship_rule_version=RELATIONSHIP_RULE_VERSION,
                entity_metrics=ent_metrics,
                relationship_metrics=rel_metrics,
                confidence_distribution=conf_dist,
                warnings=[],
                limitations=["Metrics computed against synthetic data. Not representative of production performance."]
            ))
            
        except RuntimeError as e:
            results.append(ProviderComparisonItem(
                provider=extractor.provider_name,
                provider_status="UNAVAILABLE",
                provider_version=extractor.provider_version,
                model_version=extractor.model_version,
                extraction_version=extractor.extraction_version,
                post_processing_version="1.0.0",
                relationship_rule_version=RELATIONSHIP_RULE_VERSION,
                warnings=[str(e)],
                limitations=[]
            ))
        except Exception as e:
            results.append(ProviderComparisonItem(
                provider=extractor.provider_name if hasattr(extractor, "provider_name") else provider_name,
                provider_status="FAILED",
                provider_version="N/A",
                model_version="N/A",
                extraction_version="N/A",
                post_processing_version="N/A",
                relationship_rule_version="N/A",
                warnings=[str(e)],
                limitations=[]
            ))
            
    return ProviderComparisonResult(
        dataset_version=dataset_version,
        test_document_ids=test_doc_ids,
        evaluation_timestamp=evaluation_timestamp,
        providers=results
    )

import os
import json
import logging
from typing import List, Dict, Any, Optional

try:
    import spacy
    from spacy.tokens import DocBin, Span
except ImportError:
    spacy = None

logger = logging.getLogger(__name__)

def convert_to_spacy_format(input_jsonl: str, output_path: str, model_name: str = "en_core_web_sm"):
    """Convert JSONL to spaCy binary format."""
    if spacy is None:
        raise RuntimeError("spaCy is not installed. Cannot convert dataset.")
        
    if not os.path.exists(input_jsonl):
        raise FileNotFoundError(f"Input file {input_jsonl} not found.")

    nlp = spacy.blank("en")
    doc_bin = DocBin()
    
    doc_count = 0
    entity_count = 0
    skipped_entities = 0
    
    with open(input_jsonl, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            record = json.loads(line)
            
            text = record.get("text", record.get("content", ""))
            doc = nlp.make_doc(text)
            
            entities = record.get("entities", [])
            spans = []
            
            for ent in entities:
                label = ent.get("label", ent.get("entity_type"))
                start = ent.get("start", ent.get("start_offset"))
                end = ent.get("end", ent.get("end_offset"))
                
                if start is None or end is None:
                    continue
                    
                span = doc.char_span(start, end, label=label, alignment_mode="contract")
                if span is None:
                    # Could not align exactly to tokens
                    skipped_entities += 1
                else:
                    spans.append(span)
                    
            try:
                doc.ents = spacy.util.filter_spans(spans) # Remove overlaps safely
                added = len(doc.ents)
                skipped_entities += (len(spans) - added)
                entity_count += added
                doc_bin.add(doc)
                doc_count += 1
            except Exception as e:
                logger.warning(f"Failed to process document {record.get('id')}: {e}")
                
    # Ensure output dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc_bin.to_disk(output_path)
    
    return {
        "output_path": output_path,
        "document_count": doc_count,
        "entity_count": entity_count,
        "skipped_entities": skipped_entities
    }

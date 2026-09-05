from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class LabelCounts(BaseModel):
    label: str
    count: int
    is_sufficient: bool

class SplitStatus(BaseModel):
    exists: bool
    document_count: int
    entity_count: int
    label_distribution: List[LabelCounts]

class ReadinessStatus(BaseModel):
    status: str # READY | READY_WITH_WARNINGS | NOT_READY
    dataset_version: str
    training_enabled: bool
    train_split: SplitStatus
    validation_split: SplitStatus
    test_split: SplitStatus
    warnings: List[str]
    errors: List[str]

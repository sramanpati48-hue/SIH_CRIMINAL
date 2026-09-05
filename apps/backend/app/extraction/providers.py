"""Extraction provider interfaces."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from apps.backend.app.extraction.schemas import DocumentExtractionResult

class ExtractorProvider(ABC):
    """Base class for all extraction providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def provider_version(self) -> str:
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        pass

    @property
    def extraction_version(self) -> str:
        return "1.0.0"

    @abstractmethod
    def extract(self, document_id: str, document_text: str) -> DocumentExtractionResult:
        """Extract entities and relationships from document text."""
        pass


class LLMExtractor(ExtractorProvider):
    """Placeholder for future LLM-based extraction provider."""
    
    @property
    def provider_name(self) -> str:
        return "LLM_EXTRACTOR"

    @property
    def provider_version(self) -> str:
        return "1.0.0"
        
    @property
    def model_version(self) -> str:
        return "N/A"

    def extract(self, document_id: str, document_text: str) -> DocumentExtractionResult:
        raise NotImplementedError("LLM Extractor not implemented yet.")


class HuggingFaceExtractor(ExtractorProvider):
    """Placeholder for future Hugging Face NER extraction provider."""
    
    @property
    def provider_name(self) -> str:
        return "HF_NER_EXTRACTOR"

    @property
    def provider_version(self) -> str:
        return "1.0.0"

    @property
    def model_version(self) -> str:
        return "N/A"

    def extract(self, document_id: str, document_text: str) -> DocumentExtractionResult:
        raise NotImplementedError("Hugging Face Extractor not implemented yet.")

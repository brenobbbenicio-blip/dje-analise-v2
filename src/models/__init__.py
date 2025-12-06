"""
Módulos de modelos do sistema
"""
from .rag_system import RAGSystem
from .contradiction_models import (
    JurisprudenceCase,
    SimilarCase,
    Contradiction,
    ContradictionCluster,
    ContradictionReport,
    ContradictionAlert
)
from .document_models import (
    Party,
    LegalArgument,
    Citation,
    DocumentSection,
    LegalDocument,
    DocumentTemplate,
    GenerationRequest,
    GenerationResult
)

__all__ = [
    'RAGSystem',
    'JurisprudenceCase',
    'SimilarCase',
    'Contradiction',
    'ContradictionCluster',
    'ContradictionReport',
    'ContradictionAlert',
    'Party',
    'LegalArgument',
    'Citation',
    'DocumentSection',
    'LegalDocument',
    'DocumentTemplate',
    'GenerationRequest',
    'GenerationResult'
]

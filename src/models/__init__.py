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

__all__ = [
    'RAGSystem',
    'JurisprudenceCase',
    'SimilarCase',
    'Contradiction',
    'ContradictionCluster',
    'ContradictionReport',
    'ContradictionAlert'
]

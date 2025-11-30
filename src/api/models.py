"""
Modelos Pydantic para a API
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Requisição de consulta"""
    query: str = Field(..., description="Pergunta sobre jurisprudência")
    n_results: Optional[int] = Field(5, description="Número de resultados", ge=1, le=20)
    temperature: Optional[float] = Field(0.7, description="Temperatura do modelo", ge=0, le=2)


class SearchRequest(BaseModel):
    """Requisição de busca"""
    query: str = Field(..., description="Consulta de busca")
    n_results: Optional[int] = Field(5, description="Número de resultados", ge=1, le=50)
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros de metadados")


class DocumentMetadata(BaseModel):
    """Metadados de um documento"""
    title: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None
    process_number: Optional[str] = None
    judicial_body: Optional[str] = None
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None


class SearchResult(BaseModel):
    """Resultado de busca"""
    id: str
    text: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None


class SearchResponse(BaseModel):
    """Resposta de busca"""
    query: str
    results: List[SearchResult]
    total: int


class QueryResponse(BaseModel):
    """Resposta de consulta com RAG"""
    query: str
    answer: str
    sources: List[SearchResult]
    model: str


class CollectionStats(BaseModel):
    """Estatísticas da coleção"""
    name: str
    count: int
    persist_directory: str


class SystemStats(BaseModel):
    """Estatísticas do sistema"""
    vector_store: CollectionStats
    embedding_model: str
    chat_model: str


class HealthResponse(BaseModel):
    """Resposta de health check"""
    status: str
    timestamp: datetime
    version: str


class ErrorResponse(BaseModel):
    """Resposta de erro"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime

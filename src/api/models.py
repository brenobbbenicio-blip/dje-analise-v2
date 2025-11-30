"""Modelos Pydantic para a API REST.

Define schemas de validação para requisições e respostas
dos endpoints da API.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Requisição de consulta RAG com geração de resposta."""

    query: str = Field(..., description="Pergunta sobre jurisprudência")
    n_results: int | None = Field(
        5, description="Número de documentos para contexto", ge=1, le=20
    )
    temperature: float | None = Field(
        0.7, description="Temperatura do modelo LLM", ge=0, le=2
    )


class SearchRequest(BaseModel):
    """Requisição de busca semântica simples."""

    query: str = Field(..., description="Consulta de busca")
    n_results: int | None = Field(
        5, description="Número de resultados", ge=1, le=50
    )
    filters: dict[str, Any] | None = Field(
        None, description="Filtros de metadados"
    )


class DocumentMetadata(BaseModel):
    """Metadados associados a um documento ou chunk."""

    title: str | None = None
    date: str | None = None
    url: str | None = None
    process_number: str | None = None
    judicial_body: str | None = None
    chunk_index: int | None = None
    total_chunks: int | None = None


class SearchResult(BaseModel):
    """Resultado individual de uma busca."""

    id: str
    text: str
    metadata: dict[str, Any]
    distance: float | None = None


class SearchResponse(BaseModel):
    """Resposta de busca semântica."""

    query: str
    results: list[SearchResult]
    total: int


class QueryResponse(BaseModel):
    """Resposta de consulta RAG com resposta gerada."""

    query: str
    answer: str
    sources: list[SearchResult]
    model: str


class CollectionStats(BaseModel):
    """Estatísticas da coleção de documentos."""

    name: str
    count: int
    persist_directory: str


class SystemStats(BaseModel):
    """Estatísticas gerais do sistema RAG."""

    vector_store: CollectionStats
    embedding_model: str
    chat_model: str


class HealthResponse(BaseModel):
    """Resposta de health check da API."""

    status: str
    timestamp: datetime
    version: str


class ErrorResponse(BaseModel):
    """Resposta padronizada de erro."""

    error: str
    detail: str | None = None
    timestamp: datetime

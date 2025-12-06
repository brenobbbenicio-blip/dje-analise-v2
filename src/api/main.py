"""API REST para o sistema de análise de jurisprudência eleitoral.

Implementa endpoints para busca semântica e consultas RAG
de decisões judiciais do TSE.
"""
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src import __version__
from src.api.models import (
    ErrorResponse,
    HealthResponse,
    QueryRequest,
    QueryResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    SystemStats,
)
from src.rag.rag_system import RAGSystem
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Sistema RAG (singleton)
rag_system: RAGSystem | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Gerencia o ciclo de vida da aplicação."""
    global rag_system
    try:
        logger.info("Iniciando sistema RAG...")
        rag_system = RAGSystem()
        logger.info("Sistema RAG iniciado com sucesso")
    except ValueError as e:
        logger.error(f"Erro ao iniciar sistema RAG: {e}")
        # Permite que a API inicie mesmo sem RAG configurado
    yield
    # Cleanup (se necessário)


app = FastAPI(
    title="DJE Análise v2",
    description="Sistema de análise de jurisprudência eleitoral com RAG",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root() -> HealthResponse:
    """Endpoint raiz com informações básicas da API."""
    return HealthResponse(
        status="online",
        timestamp=datetime.now(),
        version=__version__,
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check para monitoramento da API."""
    return HealthResponse(
        status="healthy" if rag_system else "degraded",
        timestamp=datetime.now(),
        version=__version__,
    )


@app.get("/stats", response_model=SystemStats, tags=["System"])
async def get_stats() -> SystemStats:
    """Retorna estatísticas do sistema RAG."""
    if not rag_system:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema RAG não inicializado",
        )

    try:
        stats = rag_system.get_stats()
        return SystemStats(**stats)
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search(request: SearchRequest) -> SearchResponse:
    """Busca semântica por documentos relevantes.

    Args:
        request: Parâmetros de busca incluindo query e filtros.

    Returns:
        Lista de documentos ordenados por relevância.
    """
    if not rag_system:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema RAG não inicializado",
        )

    try:
        results = rag_system.search(
            query=request.query,
            n_results=request.n_results,
            filter_dict=request.filters,
        )

        search_results = [
            SearchResult(
                id=r["id"],
                text=r["text"],
                metadata=r["metadata"],
                distance=r.get("distance"),
            )
            for r in results
        ]

        return SearchResponse(
            query=request.query,
            results=search_results,
            total=len(search_results),
        )

    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query(request: QueryRequest) -> QueryResponse:
    """Consulta RAG: busca documentos e gera resposta contextualizada.

    Args:
        request: Pergunta e parâmetros de geração.

    Returns:
        Resposta gerada com fontes utilizadas.
    """
    if not rag_system:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema RAG não inicializado",
        )

    try:
        response = rag_system.generate_response(
            query=request.query,
            n_results=request.n_results,
            temperature=request.temperature or 0.7,
        )

        sources = [
            SearchResult(
                id=s["id"],
                text=s["text"],
                metadata=s["metadata"],
                distance=s.get("distance"),
            )
            for s in response["sources"]
        ]

        return QueryResponse(
            query=response["query"],
            answer=response["answer"],
            sources=sources,
            model=response["model"],
        )

    except Exception as e:
        logger.error(f"Erro na consulta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handler global para exceções não tratadas."""
    logger.error(f"Erro não tratado: {exc}")
    error_response = ErrorResponse(
        error="Internal Server Error",
        detail=str(exc),
        timestamp=datetime.now(),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode="json"),
    )


if __name__ == "__main__":
    import uvicorn

    from src.config import settings

    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )

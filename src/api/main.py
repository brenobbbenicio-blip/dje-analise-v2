"""
API REST para o sistema de análise de jurisprudência
"""
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src import __version__
from src.config import settings
from src.rag.rag_system import RAGSystem
from src.api.models import (
    QueryRequest,
    QueryResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    SystemStats,
    HealthResponse,
    ErrorResponse
)
from src.utils.logger import setup_logger


logger = setup_logger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="DJE Análise v2",
    description="Sistema de análise de jurisprudência eleitoral com RAG",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sistema RAG (singleton)
rag_system: Optional[RAGSystem] = None


@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação"""
    global rag_system
    try:
        logger.info("Iniciando sistema RAG...")
        rag_system = RAGSystem()
        logger.info("Sistema RAG iniciado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao iniciar sistema RAG: {e}")
        # Permitir que a API inicie mesmo sem RAG configurado
        # para que possamos ver documentação e health check


@app.get(
    "/",
    response_model=HealthResponse,
    tags=["Health"]
)
async def root():
    """Endpoint raiz com informações da API"""
    return HealthResponse(
        status="online",
        timestamp=datetime.now(),
        version=__version__
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"]
)
async def health_check():
    """Health check da API"""
    return HealthResponse(
        status="healthy" if rag_system else "degraded",
        timestamp=datetime.now(),
        version=__version__
    )


@app.get(
    "/stats",
    response_model=SystemStats,
    tags=["System"]
)
async def get_stats():
    """Retorna estatísticas do sistema"""
    if not rag_system:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema RAG não inicializado"
        )

    try:
        stats = rag_system.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post(
    "/search",
    response_model=SearchResponse,
    tags=["Search"]
)
async def search(request: SearchRequest):
    """
    Busca semântica por documentos similares

    Args:
        request: Parâmetros de busca

    Returns:
        Documentos relevantes
    """
    if not rag_system:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema RAG não inicializado"
        )

    try:
        results = rag_system.search(
            query=request.query,
            n_results=request.n_results,
            filter_dict=request.filters
        )

        search_results = [
            SearchResult(
                id=r['id'],
                text=r['text'],
                metadata=r['metadata'],
                distance=r.get('distance')
            )
            for r in results
        ]

        return SearchResponse(
            query=request.query,
            results=search_results,
            total=len(search_results)
        )

    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post(
    "/query",
    response_model=QueryResponse,
    tags=["Query"]
)
async def query(request: QueryRequest):
    """
    Consulta com RAG - gera resposta baseada nos documentos

    Args:
        request: Parâmetros da consulta

    Returns:
        Resposta gerada com fontes
    """
    if not rag_system:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema RAG não inicializado"
        )

    try:
        response = rag_system.generate_response(
            query=request.query,
            n_results=request.n_results,
            temperature=request.temperature
        )

        sources = [
            SearchResult(
                id=s['id'],
                text=s['text'],
                metadata=s['metadata'],
                distance=s.get('distance')
            )
            for s in response['sources']
        ]

        return QueryResponse(
            query=response['query'],
            answer=response['answer'],
            sources=sources,
            model=response['model']
        )

    except Exception as e:
        logger.error(f"Erro na consulta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global de exceções"""
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            timestamp=datetime.now()
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )

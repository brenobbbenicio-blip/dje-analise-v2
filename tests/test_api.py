"""Testes dos endpoints da API REST.

Verifica o funcionamento correto dos endpoints de health check,
busca e consulta do sistema.
"""
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_root() -> None:
    """Teste do endpoint raiz."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["online", "degraded"]
    assert "version" in data


def test_health_check() -> None:
    """Teste do health check."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]


def test_docs() -> None:
    """Teste da documentação Swagger."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_search_without_rag() -> None:
    """Teste de busca sem sistema RAG inicializado."""
    response = client.post(
        "/search",
        json={"query": "eleições", "n_results": 5},
    )
    # Retorna 503 se RAG não estiver configurado
    assert response.status_code in [200, 503]


def test_query_without_rag() -> None:
    """Teste de consulta sem sistema RAG inicializado."""
    response = client.post(
        "/query",
        json={
            "query": "Como funciona a prestação de contas?",
            "n_results": 5,
            "temperature": 0.7,
        },
    )
    # Retorna 503 se RAG não estiver configurado
    assert response.status_code in [200, 503]


def test_invalid_search_params() -> None:
    """Teste com parâmetros inválidos na busca."""
    response = client.post(
        "/search",
        json={"query": "teste", "n_results": 100},  # Excede limite de 50
    )
    assert response.status_code == 422  # Validation error

"""
Testes da API
"""
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_root():
    """Teste do endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["online", "degraded"]
    assert "version" in data


def test_health_check():
    """Teste do health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]


def test_docs():
    """Teste da documentação"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_search_without_rag():
    """Teste de busca sem sistema RAG inicializado"""
    response = client.post(
        "/search",
        json={"query": "eleições", "n_results": 5}
    )
    # Pode retornar 503 se RAG não estiver configurado
    assert response.status_code in [200, 503]


def test_query_without_rag():
    """Teste de consulta sem sistema RAG inicializado"""
    response = client.post(
        "/query",
        json={
            "query": "Como funciona a prestação de contas?",
            "n_results": 5,
            "temperature": 0.7
        }
    )
    # Pode retornar 503 se RAG não estiver configurado
    assert response.status_code in [200, 503]


def test_invalid_search_params():
    """Teste com parâmetros inválidos"""
    response = client.post(
        "/search",
        json={"query": "teste", "n_results": 100}  # Excede limite
    )
    assert response.status_code == 422  # Validation error

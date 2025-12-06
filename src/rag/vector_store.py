"""Armazenamento vetorial usando ChromaDB.

Implementa persistência e busca semântica de documentos
usando vetores de embedding.
"""
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.api.types import QueryResult
from chromadb.config import Settings as ChromaSettings

from src.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# Tipo para metadados compatível com ChromaDB
Metadata = dict[str, str | int | float | bool]


class VectorStore:
    """Armazenamento vetorial para busca semântica de jurisprudências.

    Utiliza ChromaDB para persistir embeddings e realizar buscas
    por similaridade vetorial.
    """

    def __init__(
        self,
        persist_directory: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        """Inicializa o vector store com ChromaDB.

        Args:
            persist_directory: Diretório para persistência (usa settings se None).
            collection_name: Nome da coleção (usa settings se None).
        """
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIR
        self.collection_name = collection_name or settings.COLLECTION_NAME

        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        self.collection: Collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Jurisprudência eleitoral do DJE"},
        )

        logger.info(f"VectorStore inicializado: {self.collection_name}")

    def add_documents(
        self,
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[Metadata],
        ids: list[str] | None = None,
    ) -> None:
        """Adiciona documentos ao armazenamento vetorial.

        Args:
            texts: Lista de textos dos documentos.
            embeddings: Lista de vetores de embedding.
            metadatas: Lista de metadados associados.
            ids: IDs únicos (gerados automaticamente se não fornecidos).

        Raises:
            chromadb.errors.ChromaError: Se houver erro na inserção.
        """
        if not ids:
            ids = [f"doc_{i}" for i in range(len(texts))]

        try:
            self.collection.add(
                documents=texts,
                embeddings=embeddings,  # type: ignore[arg-type]
                metadatas=metadatas,  # type: ignore[arg-type]
                ids=ids,
            )
            logger.info(f"Adicionados {len(texts)} documentos ao vector store")
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos: {e}")
            raise

    def search(
        self,
        query_embedding: list[float],
        n_results: int | None = None,
        filter_dict: dict[str, Any] | None = None,
    ) -> QueryResult:
        """Busca documentos similares por embedding.

        Args:
            query_embedding: Vetor de embedding da consulta.
            n_results: Número de resultados (usa TOP_K_RESULTS se None).
            filter_dict: Filtros de metadados opcionais.

        Returns:
            Resultados da busca com IDs, documentos, metadados e distâncias.

        Raises:
            chromadb.errors.ChromaError: Se houver erro na busca.
        """
        n_results = n_results or settings.TOP_K_RESULTS

        try:
            results: QueryResult = self.collection.query(
                query_embeddings=[query_embedding],  # type: ignore[arg-type]
                n_results=n_results,
                where=filter_dict,
            )
            return results
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            raise

    def delete_collection(self) -> None:
        """Deleta a coleção do ChromaDB."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Coleção {self.collection_name} deletada")
        except Exception as e:
            logger.error(f"Erro ao deletar coleção: {e}")

    def get_collection_stats(self) -> dict[str, Any]:
        """Retorna estatísticas da coleção.

        Returns:
            Dicionário com nome, contagem e diretório de persistência.
        """
        count = self.collection.count()
        return {
            "name": self.collection_name,
            "count": count,
            "persist_directory": self.persist_directory,
        }

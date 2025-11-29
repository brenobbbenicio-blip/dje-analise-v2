"""
Armazenamento vetorial usando ChromaDB
"""
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from src.config import settings
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class VectorStore:
    """Armazenamento vetorial para busca semântica"""

    def __init__(self, persist_directory: str = None, collection_name: str = None):
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIR
        self.collection_name = collection_name or settings.COLLECTION_NAME

        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Criar ou obter coleção
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Jurisprudência eleitoral do DJE"}
        )

        logger.info(f"VectorStore inicializado: {self.collection_name}")

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ):
        """
        Adiciona documentos ao armazenamento

        Args:
            texts: Lista de textos
            embeddings: Lista de embeddings
            metadatas: Lista de metadados
            ids: IDs dos documentos (gerados se não fornecidos)
        """
        if not ids:
            ids = [f"doc_{i}" for i in range(len(texts))]

        try:
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Adicionados {len(texts)} documentos ao vector store")
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos: {e}")
            raise

    def search(
        self,
        query_embedding: List[float],
        n_results: int = None,
        filter_dict: Optional[Dict] = None
    ) -> Dict:
        """
        Busca documentos similares

        Args:
            query_embedding: Embedding da consulta
            n_results: Número de resultados
            filter_dict: Filtros de metadados

        Returns:
            Resultados da busca
        """
        n_results = n_results or settings.TOP_K_RESULTS

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_dict
            )
            return results
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            raise

    def delete_collection(self):
        """Deleta a coleção"""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Coleção {self.collection_name} deletada")
        except Exception as e:
            logger.error(f"Erro ao deletar coleção: {e}")

    def get_collection_stats(self) -> Dict:
        """
        Retorna estatísticas da coleção

        Returns:
            Dicionário com estatísticas
        """
        count = self.collection.count()
        return {
            "name": self.collection_name,
            "count": count,
            "persist_directory": self.persist_directory
        }

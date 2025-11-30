"""Sistema RAG completo para análise de jurisprudência eleitoral.

Implementa o pipeline de Retrieval-Augmented Generation,
combinando busca semântica com geração de respostas via LLM.
"""
from typing import Any

import openai

from src.config import settings
from src.rag.embeddings import EmbeddingGenerator
from src.rag.vector_store import VectorStore
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class RAGSystem:
    """Sistema completo de RAG para jurisprudência eleitoral.

    Integra geração de embeddings, armazenamento vetorial e
    geração de respostas com contexto.
    """

    def __init__(self, api_key: str | None = None) -> None:
        """Inicializa o sistema RAG com todas as dependências.

        Args:
            api_key: Chave da API OpenAI (usa settings se não fornecida).

        Raises:
            ValueError: Se a chave de API não estiver configurada.
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key não configurada")

        openai.api_key = self.api_key

        self.embedding_generator = EmbeddingGenerator(api_key=self.api_key)
        self.vector_store = VectorStore()
        self.model = settings.OPENAI_MODEL

        logger.info("Sistema RAG inicializado")

    def index_documents(self, chunks: list[dict[str, Any]]) -> None:
        """Indexa documentos no vector store para busca posterior.

        Args:
            chunks: Lista de chunks com 'text' e 'metadata'.
        """
        logger.info(f"Indexando {len(chunks)} chunks")

        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        logger.info("Gerando embeddings...")
        embeddings = self.embedding_generator.generate_embeddings_batch(texts)

        ids = [
            f"chunk_{i}_{chunk['metadata'].get('chunk_index', 0)}"
            for i, chunk in enumerate(chunks)
        ]

        self.vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info("Indexação concluída")

    def search(
        self,
        query: str,
        n_results: int | None = None,
        filter_dict: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Busca documentos relevantes para uma consulta.

        Args:
            query: Consulta em linguagem natural.
            n_results: Número de resultados desejados.
            filter_dict: Filtros opcionais de metadados.

        Returns:
            Lista de documentos com id, text, metadata e distance.
        """
        logger.info(f"Buscando: {query}")

        query_embedding = self.embedding_generator.generate_embedding(query)

        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
            filter_dict=filter_dict,
        )

        formatted_results: list[dict[str, Any]] = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                distance: float | None = None
                distances = results.get("distances")
                if distances is not None and distances[0]:
                    distance = distances[0][i]

                result_item: dict[str, Any] = {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i] if results["documents"] else "",
                    "metadata": (
                        results["metadatas"][0][i] if results["metadatas"] else {}
                    ),
                    "distance": distance,
                }
                formatted_results.append(result_item)

        return formatted_results

    def generate_response(
        self,
        query: str,
        n_results: int | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Gera resposta usando RAG: busca + geração com contexto.

        Args:
            query: Pergunta do usuário.
            n_results: Número de documentos para contexto.
            temperature: Criatividade do modelo (0.0 a 2.0).

        Returns:
            Dicionário com query, answer, sources e model.

        Raises:
            openai.OpenAIError: Se a geração falhar.
        """
        logger.info(f"Gerando resposta para: {query}")

        relevant_docs = self.search(query, n_results=n_results)

        context = "\n\n".join([
            f"[Documento {i + 1}]\n{doc['text']}"
            for i, doc in enumerate(relevant_docs)
        ])

        system_prompt = (
            "Você é um assistente especializado em jurisprudência eleitoral "
            "brasileira. Sua função é analisar decisões judiciais e fornecer "
            "informações precisas baseadas nos documentos fornecidos. "
            "Sempre cite as fontes e seja objetivo nas respostas."
        )

        user_prompt = f"""Com base nos seguintes documentos de jurisprudência eleitoral:

{context}

Responda à seguinte pergunta:
{query}

Se a informação não estiver nos documentos fornecidos, indique claramente."""

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )

            answer = response.choices[0].message.content or ""

            return {
                "query": query,
                "answer": answer,
                "sources": relevant_docs,
                "model": self.model,
            }

        except openai.OpenAIError as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            raise

    def get_stats(self) -> dict[str, Any]:
        """Retorna estatísticas do sistema RAG.

        Returns:
            Dicionário com estatísticas do vector store e modelos usados.
        """
        return {
            "vector_store": self.vector_store.get_collection_stats(),
            "embedding_model": self.embedding_generator.model,
            "chat_model": self.model,
        }

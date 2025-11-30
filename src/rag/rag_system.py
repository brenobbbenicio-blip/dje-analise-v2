"""
Sistema RAG completo para análise de jurisprudência
"""
from typing import List, Dict, Optional
import openai

from src.config import settings
from src.rag.embeddings import EmbeddingGenerator
from src.rag.vector_store import VectorStore
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class RAGSystem:
    """Sistema completo de RAG para jurisprudência eleitoral"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key não configurada")

        openai.api_key = self.api_key

        self.embedding_generator = EmbeddingGenerator(api_key=self.api_key)
        self.vector_store = VectorStore()
        self.model = settings.OPENAI_MODEL

        logger.info("Sistema RAG inicializado")

    def index_documents(self, chunks: List[Dict[str, any]]):
        """
        Indexa documentos no vector store

        Args:
            chunks: Lista de chunks processados com texto e metadados
        """
        logger.info(f"Indexando {len(chunks)} chunks")

        # Extrair textos e metadados
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]

        # Gerar embeddings
        logger.info("Gerando embeddings...")
        embeddings = self.embedding_generator.generate_embeddings_batch(texts)

        # Gerar IDs únicos
        ids = [f"chunk_{i}_{chunk['metadata'].get('chunk_index', 0)}"
               for i, chunk in enumerate(chunks)]

        # Adicionar ao vector store
        self.vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        logger.info("Indexação concluída")

    def search(
        self,
        query: str,
        n_results: int = None,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Busca documentos relevantes

        Args:
            query: Consulta em linguagem natural
            n_results: Número de resultados
            filter_dict: Filtros de metadados

        Returns:
            Lista de documentos relevantes
        """
        logger.info(f"Buscando: {query}")

        # Gerar embedding da consulta
        query_embedding = self.embedding_generator.generate_embedding(query)

        # Buscar no vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
            filter_dict=filter_dict
        )

        # Formatar resultados
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })

        return formatted_results

    def generate_response(
        self,
        query: str,
        n_results: int = None,
        temperature: float = 0.7
    ) -> Dict[str, any]:
        """
        Gera resposta usando RAG

        Args:
            query: Pergunta do usuário
            n_results: Número de documentos para contexto
            temperature: Temperatura do modelo

        Returns:
            Dicionário com resposta e contexto
        """
        logger.info(f"Gerando resposta para: {query}")

        # Buscar documentos relevantes
        relevant_docs = self.search(query, n_results=n_results)

        # Construir contexto
        context = "\n\n".join([
            f"[Documento {i+1}]\n{doc['text']}"
            for i, doc in enumerate(relevant_docs)
        ])

        # Construir prompt
        system_prompt = """Você é um assistente especializado em jurisprudência eleitoral brasileira.
Sua função é analisar decisões judiciais e fornecer informações precisas baseadas nos documentos fornecidos.
Sempre cite as fontes e seja objetivo nas respostas."""

        user_prompt = f"""Com base nos seguintes documentos de jurisprudência eleitoral:

{context}

Responda à seguinte pergunta:
{query}

Se a informação não estiver nos documentos fornecidos, indique claramente."""

        # Gerar resposta
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )

            answer = response.choices[0].message.content

            return {
                "query": query,
                "answer": answer,
                "sources": relevant_docs,
                "model": self.model
            }

        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            raise

    def get_stats(self) -> Dict:
        """
        Retorna estatísticas do sistema

        Returns:
            Dicionário com estatísticas
        """
        return {
            "vector_store": self.vector_store.get_collection_stats(),
            "embedding_model": self.embedding_generator.model,
            "chat_model": self.model
        }

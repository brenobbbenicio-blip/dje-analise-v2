"""
Sistema RAG (Retrieval-Augmented Generation) para análise de jurisprudência
"""
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from openai import OpenAI

from src.config import (
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    CHAT_MODEL,
    VECTORSTORE_DIR,
    CHROMA_COLLECTION_NAME,
    MAX_TOKENS,
    TEMPERATURE
)


class RAGSystem:
    """Sistema RAG para consulta de jurisprudência eleitoral"""

    def __init__(self):
        """Inicializa o sistema RAG"""
        self.client = OpenAI(api_key=OPENAI_API_KEY)

        # Inicializar ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(VECTORSTORE_DIR),
            settings=Settings(anonymized_telemetry=False)
        )

        # Obter ou criar coleção
        try:
            self.collection = self.chroma_client.get_collection(
                name=CHROMA_COLLECTION_NAME
            )
        except:
            self.collection = self.chroma_client.create_collection(
                name=CHROMA_COLLECTION_NAME,
                metadata={"description": "Jurisprudência eleitoral brasileira"}
            )

    def get_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um texto

        Args:
            text: Texto para gerar embedding

        Returns:
            Lista de floats representando o embedding
        """
        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Adiciona documentos ao vectorstore

        Args:
            documents: Lista de dicionários com 'text', 'metadata'
        """
        texts = [doc['text'] for doc in documents]
        metadatas = [doc.get('metadata', {}) for doc in documents]
        ids = [f"doc_{i}" for i in range(len(documents))]

        # Gerar embeddings
        embeddings = [self.get_embedding(text) for text in texts]

        # Adicionar à coleção
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def search(
        self,
        query: str,
        n_results: int = 5,
        tribunal_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Busca documentos relevantes

        Args:
            query: Consulta do usuário
            n_results: Número de resultados a retornar
            tribunal_filter: Filtrar por tribunal específico (opcional)

        Returns:
            Lista de documentos relevantes com metadados
        """
        query_embedding = self.get_embedding(query)

        # Preparar filtro se tribunal foi especificado
        where_filter = None
        if tribunal_filter:
            where_filter = {"tribunal": tribunal_filter}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )

        documents = []
        for i in range(len(results['documents'][0])):
            documents.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })

        return documents

    def generate_answer(
        self,
        query: str,
        context_docs: List[Dict],
        max_tokens: int = MAX_TOKENS
    ) -> str:
        """
        Gera resposta usando RAG

        Args:
            query: Pergunta do usuário
            context_docs: Documentos de contexto
            max_tokens: Máximo de tokens na resposta

        Returns:
            Resposta gerada
        """
        # Construir contexto
        context = "\n\n".join([
            f"Documento {i+1}:\n{doc['text']}"
            for i, doc in enumerate(context_docs)
        ])

        # Criar prompt
        system_prompt = """Você é um assistente especializado em jurisprudência eleitoral brasileira.
Use os documentos fornecidos para responder às perguntas de forma precisa e fundamentada.
Sempre cite os trechos relevantes da jurisprudência ao responder."""

        user_prompt = f"""Contexto (jurisprudência eleitoral):
{context}

Pergunta: {query}

Responda de forma clara e objetiva, citando os trechos relevantes da jurisprudência."""

        # Gerar resposta
        response = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=TEMPERATURE
        )

        return response.choices[0].message.content

    def query(
        self,
        question: str,
        n_results: int = 5,
        tribunal_filter: Optional[str] = None
    ) -> Dict:
        """
        Pipeline completo de consulta RAG

        Args:
            question: Pergunta do usuário
            n_results: Número de documentos a recuperar
            tribunal_filter: Filtrar por tribunal específico (opcional)

        Returns:
            Dicionário com resposta e documentos fonte
        """
        # 1. Buscar documentos relevantes
        relevant_docs = self.search(
            question,
            n_results=n_results,
            tribunal_filter=tribunal_filter
        )

        # 2. Gerar resposta
        answer = self.generate_answer(question, relevant_docs)

        result = {
            'answer': answer,
            'sources': relevant_docs,
            'query': question
        }

        if tribunal_filter:
            result['tribunal_filter'] = tribunal_filter

        return result

    def get_stats(self, by_tribunal: bool = False) -> Dict:
        """
        Retorna estatísticas da base de dados

        Args:
            by_tribunal: Se True, retorna contagem por tribunal

        Returns:
            Dicionário com estatísticas
        """
        count = self.collection.count()
        stats = {
            'total_documents': count,
            'collection_name': CHROMA_COLLECTION_NAME
        }

        if by_tribunal and count > 0:
            # Contar documentos por tribunal
            from src.config import AVAILABLE_TRIBUNALS

            tribunal_counts = {}
            for tribunal in AVAILABLE_TRIBUNALS:
                try:
                    results = self.collection.get(
                        where={"tribunal": tribunal}
                    )
                    tribunal_counts[tribunal] = len(results['ids'])
                except:
                    tribunal_counts[tribunal] = 0

            stats['by_tribunal'] = tribunal_counts

        return stats

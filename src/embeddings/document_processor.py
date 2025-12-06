"""
Processador de documentos para criar embeddings e chunks
"""
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_SIZE, CHUNK_OVERLAP


class DocumentProcessor:
    """Processa documentos para o sistema RAG"""

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP
    ):
        """
        Inicializa o processador

        Args:
            chunk_size: Tamanho dos chunks
            chunk_overlap: Sobreposição entre chunks
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def process_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Processa documentos criando chunks e preparando para embeddings

        Args:
            documents: Lista de documentos com 'text' e 'metadata'

        Returns:
            Lista de chunks processados
        """
        processed_docs = []

        for doc in documents:
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})

            # Adicionar título ao texto se disponível
            if 'title' in doc:
                text = f"{doc['title']}\n\n{text}"
                metadata['title'] = doc['title']

            # Criar chunks
            chunks = self.text_splitter.split_text(text)

            # Adicionar cada chunk com metadata
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_id'] = i
                chunk_metadata['total_chunks'] = len(chunks)

                processed_docs.append({
                    'text': chunk,
                    'metadata': chunk_metadata
                })

        return processed_docs

    def clean_text(self, text: str) -> str:
        """
        Limpa e normaliza texto

        Args:
            text: Texto a ser limpo

        Returns:
            Texto limpo
        """
        # Remover espaços extras
        text = ' '.join(text.split())

        # Remover caracteres especiais problemáticos
        text = text.replace('\x00', '')

        return text.strip()

    def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """
        Extrai palavras-chave do texto (implementação simples)

        Args:
            text: Texto para extrair palavras-chave
            top_k: Número de palavras-chave

        Returns:
            Lista de palavras-chave
        """
        # Implementação simples - pode ser melhorada com NLP
        words = text.lower().split()

        # Remover palavras comuns (stopwords básicas)
        stopwords = {
            'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'do', 'da', 'dos', 'das',
            'e', 'é', 'em', 'para', 'com', 'por', 'que', 'se', 'na', 'no'
        }

        words = [w for w in words if w not in stopwords and len(w) > 3]

        # Contar frequência
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Ordenar por frequência
        sorted_words = sorted(
            word_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [word for word, freq in sorted_words[:top_k]]

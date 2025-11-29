"""
Processador de texto para jurisprudências
"""
import re
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import settings
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class TextProcessor:
    """Processador de texto para jurisprudências"""

    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def clean_text(self, text: str) -> str:
        """
        Limpa e normaliza texto

        Args:
            text: Texto a ser limpo

        Returns:
            Texto limpo
        """
        # Remove múltiplos espaços
        text = re.sub(r'\s+', ' ', text)

        # Remove caracteres especiais mantendo pontuação básica
        text = re.sub(r'[^\w\s\.,;:!?()-]', '', text)

        # Remove linhas vazias
        text = re.sub(r'\n\s*\n', '\n', text)

        return text.strip()

    def extract_metadata(self, decision: Dict[str, str]) -> Dict[str, str]:
        """
        Extrai metadados da decisão

        Args:
            decision: Decisão a processar

        Returns:
            Dicionário com metadados
        """
        metadata = {
            'title': decision.get('title', ''),
            'date': decision.get('date', ''),
            'url': decision.get('url', ''),
            'collected_at': decision.get('collected_at', '')
        }

        # Extrair número do processo se presente
        content = decision.get('content', '')
        process_match = re.search(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', content)
        if process_match:
            metadata['process_number'] = process_match.group()

        # Extrair órgão julgador
        orgao_match = re.search(r'(Tribunal|Juiz|Juíza|Relator|Relatora):?\s*([^\n]+)', content)
        if orgao_match:
            metadata['judicial_body'] = orgao_match.group(2).strip()

        return metadata

    def chunk_text(self, text: str, metadata: Dict[str, str]) -> List[Dict[str, any]]:
        """
        Divide texto em chunks com metadados

        Args:
            text: Texto a dividir
            metadata: Metadados associados

        Returns:
            Lista de chunks com metadados
        """
        cleaned_text = self.clean_text(text)
        chunks = self.text_splitter.split_text(cleaned_text)

        result = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                'text': chunk,
                'metadata': {
                    **metadata,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
            }
            result.append(chunk_data)

        logger.info(f"Texto dividido em {len(result)} chunks")
        return result

    def process_decision(self, decision: Dict[str, str]) -> List[Dict[str, any]]:
        """
        Processa uma decisão completa

        Args:
            decision: Decisão a processar

        Returns:
            Lista de chunks processados
        """
        content = decision.get('content', '')
        if not content:
            logger.warning("Decisão sem conteúdo")
            return []

        metadata = self.extract_metadata(decision)
        chunks = self.chunk_text(content, metadata)

        return chunks

    def process_batch(self, decisions: List[Dict[str, str]]) -> List[Dict[str, any]]:
        """
        Processa lote de decisões

        Args:
            decisions: Lista de decisões

        Returns:
            Lista de todos os chunks processados
        """
        all_chunks = []

        for i, decision in enumerate(decisions):
            logger.info(f"Processando decisão {i+1}/{len(decisions)}")
            chunks = self.process_decision(decision)
            all_chunks.extend(chunks)

        logger.info(f"Total de chunks processados: {len(all_chunks)}")
        return all_chunks

"""Processador de texto para jurisprudências.

Implementa limpeza, normalização e chunking de textos jurídicos
para preparação de dados para o sistema RAG.
"""
import re
from typing import Any

from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TextProcessor:
    """Processador de texto para jurisprudências eleitorais.

    Realiza limpeza, extração de metadados e divisão em chunks
    de textos de decisões judiciais.
    """

    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
    ) -> None:
        """Inicializa o processador com configurações de chunking.

        Args:
            chunk_size: Tamanho máximo de cada chunk em caracteres.
            chunk_overlap: Sobreposição entre chunks consecutivos.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def clean_text(self, text: str) -> str:
        """Limpa e normaliza texto removendo ruídos.

        Args:
            text: Texto a ser limpo.

        Returns:
            Texto normalizado sem espaços extras ou caracteres especiais.
        """
        # Remove múltiplos espaços
        text = re.sub(r"\s+", " ", text)

        # Remove caracteres especiais mantendo pontuação básica
        text = re.sub(r"[^\w\s\.,;:!?()-]", "", text)

        # Remove linhas vazias múltiplas
        text = re.sub(r"\n\s*\n", "\n", text)

        return text.strip()

    def extract_metadata(self, decision: dict[str, str]) -> dict[str, str]:
        """Extrai metadados relevantes de uma decisão.

        Args:
            decision: Dicionário com dados da decisão.

        Returns:
            Dicionário com metadados extraídos e normalizados.
        """
        metadata: dict[str, str] = {
            "title": decision.get("title", ""),
            "date": decision.get("date", ""),
            "url": decision.get("url", ""),
            "collected_at": decision.get("collected_at", ""),
        }

        content = decision.get("content", "")

        # Extrai número do processo (formato CNJ)
        process_match = re.search(
            r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}",
            content,
        )
        if process_match:
            metadata["process_number"] = process_match.group()

        # Extrai órgão julgador
        orgao_match = re.search(
            r"(Tribunal|Juiz|Juíza|Relator|Relatora):?\s*([^\n]+)",
            content,
        )
        if orgao_match:
            metadata["judicial_body"] = orgao_match.group(2).strip()

        return metadata

    def chunk_text(
        self,
        text: str,
        metadata: dict[str, str],
    ) -> list[dict[str, Any]]:
        """Divide texto em chunks com metadados associados.

        Args:
            text: Texto a dividir.
            metadata: Metadados base para associar aos chunks.

        Returns:
            Lista de chunks, cada um com texto e metadados.
        """
        cleaned_text = self.clean_text(text)
        chunks = self.text_splitter.split_text(cleaned_text)

        result: list[dict[str, Any]] = []
        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):
            chunk_data: dict[str, Any] = {
                "text": chunk,
                "metadata": {
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": total_chunks,
                },
            }
            result.append(chunk_data)

        logger.info(f"Texto dividido em {len(result)} chunks")
        return result

    def process_decision(self, decision: dict[str, str]) -> list[dict[str, Any]]:
        """Processa uma decisão completa: extrai metadados e cria chunks.

        Args:
            decision: Decisão judicial a processar.

        Returns:
            Lista de chunks processados com metadados.
        """
        content = decision.get("content", "")
        if not content:
            logger.warning("Decisão sem conteúdo")
            return []

        metadata = self.extract_metadata(decision)
        chunks = self.chunk_text(content, metadata)

        return chunks

    def process_batch(
        self,
        decisions: list[dict[str, str]],
    ) -> list[dict[str, Any]]:
        """Processa lote de decisões de forma eficiente.

        Args:
            decisions: Lista de decisões a processar.

        Returns:
            Lista consolidada de todos os chunks processados.
        """
        all_chunks: list[dict[str, Any]] = []
        total = len(decisions)

        for i, decision in enumerate(decisions, 1):
            logger.info(f"Processando decisão {i}/{total}")
            chunks = self.process_decision(decision)
            all_chunks.extend(chunks)

        logger.info(f"Total de chunks processados: {len(all_chunks)}")
        return all_chunks

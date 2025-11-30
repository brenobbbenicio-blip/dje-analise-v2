"""Coletor de dados do Diário da Justiça Eletrônica (DJE).

Este módulo implementa a coleta de decisões judiciais do TSE,
incluindo scraping de páginas HTML e extração de texto de PDFs.
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import PyPDF2
import requests
from bs4 import BeautifulSoup

from src.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DJECollector:
    """Coletor de jurisprudências do DJE do TSE.

    Realiza scraping do site do TSE para coletar decisões judiciais,
    com suporte a retry automático e rate limiting.
    """

    def __init__(self) -> None:
        """Inicializa o coletor com configurações padrão."""
        self.base_url = settings.DJE_BASE_URL
        self.timeout = settings.REQUEST_TIMEOUT
        self.max_retries = settings.MAX_RETRIES
        self.rate_limit_delay = settings.RATE_LIMIT_DELAY
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            ),
        })

    def fetch_page(self, url: str) -> str | None:
        """Faz requisição HTTP com retry exponencial.

        Args:
            url: URL para fazer a requisição.

        Returns:
            Conteúdo HTML da página ou None se todas as tentativas falharem.
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponencial
                else:
                    logger.error(
                        f"Falha ao buscar {url} após {self.max_retries} tentativas"
                    )
        return None

    def extract_pdf_text(self, pdf_path: Path) -> str:
        """Extrai texto de um arquivo PDF.

        Args:
            pdf_path: Caminho para o arquivo PDF.

        Returns:
            Texto extraído do PDF ou string vazia em caso de erro.
        """
        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_parts: list[str] = []
                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_parts.append(extracted)
                return "\n".join(text_parts)
        except (OSError, PyPDF2.errors.PdfReadError) as e:
            logger.error(f"Erro ao extrair texto do PDF {pdf_path}: {e}")
            return ""

    def parse_decision(self, html_content: str) -> list[dict[str, str]]:
        """Processa HTML e extrai decisões judiciais.

        Args:
            html_content: Conteúdo HTML da página.

        Returns:
            Lista de decisões extraídas com seus metadados.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        decisions: list[dict[str, str]] = []

        articles = soup.find_all("article", class_="decision")
        for article in articles:
            try:
                h2_tag = article.find("h2")
                time_tag = article.find("time")
                content_div = article.find("div", class_="content")
                link_tag = article.find("a")

                decision: dict[str, str] = {
                    "title": h2_tag.get_text(strip=True) if h2_tag else "",
                    "date": time_tag.get("datetime", "") if time_tag else "",
                    "content": (
                        content_div.get_text(strip=True) if content_div else ""
                    ),
                    "url": link_tag.get("href", "") if link_tag else "",
                    "collected_at": datetime.now().isoformat(),
                }
                decisions.append(decision)
            except AttributeError as e:
                logger.warning(f"Erro ao processar decisão: {e}")
                continue

        return decisions

    def collect_decisions(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        max_pages: int = 10,
    ) -> list[dict[str, str]]:
        """Coleta decisões do DJE em um intervalo de datas.

        Args:
            start_date: Data inicial (padrão: 30 dias atrás).
            end_date: Data final (padrão: hoje).
            max_pages: Número máximo de páginas a coletar.

        Returns:
            Lista de todas as decisões coletadas.
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        logger.info(f"Coletando decisões de {start_date} até {end_date}")

        all_decisions: list[dict[str, str]] = []

        for page in range(1, max_pages + 1):
            logger.info(f"Coletando página {page}/{max_pages}")

            url = f"{self.base_url}?page={page}"

            html_content = self.fetch_page(url)
            if not html_content:
                logger.warning(f"Pulando página {page}")
                continue

            decisions = self.parse_decision(html_content)
            all_decisions.extend(decisions)

            logger.info(f"Coletadas {len(decisions)} decisões da página {page}")

            # Rate limiting
            time.sleep(self.rate_limit_delay)

        return all_decisions

    def save_decisions(
        self,
        decisions: list[dict[str, str]],
        filename: str | None = None,
    ) -> Path:
        """Salva decisões em arquivo JSON.

        Args:
            decisions: Lista de decisões a salvar.
            filename: Nome do arquivo (gerado automaticamente se não fornecido).

        Returns:
            Caminho do arquivo salvo.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"decisions_{timestamp}.json"

        output_path = settings.RAW_DATA_DIR / filename

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(decisions, f, ensure_ascii=False, indent=2)

        logger.info(f"Salvas {len(decisions)} decisões em {output_path}")
        return output_path


def main() -> None:
    """Função principal para execução direta do módulo."""
    collector = DJECollector()
    decisions = collector.collect_decisions(max_pages=5)
    collector.save_decisions(decisions)
    logger.info(f"Coleta concluída: {len(decisions)} decisões")


if __name__ == "__main__":
    main()

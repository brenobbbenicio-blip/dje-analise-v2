"""
Coletor de dados do Diário da Justiça Eletrônica (DJE)
"""
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import PyPDF2
import json

from src.config import settings
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class DJECollector:
    """Coletor de jurisprudências do DJE"""

    def __init__(self):
        self.base_url = settings.DJE_BASE_URL
        self.timeout = settings.REQUEST_TIMEOUT
        self.max_retries = settings.MAX_RETRIES
        self.rate_limit_delay = settings.RATE_LIMIT_DELAY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Faz requisição HTTP com retry

        Args:
            url: URL para fazer a requisição

        Returns:
            Conteúdo HTML da página ou None se falhar
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Falha ao buscar {url} após {self.max_retries} tentativas")
                    return None

    def extract_pdf_text(self, pdf_path: Path) -> str:
        """
        Extrai texto de um arquivo PDF

        Args:
            pdf_path: Caminho para o arquivo PDF

        Returns:
            Texto extraído do PDF
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF {pdf_path}: {e}")
            return ""

    def parse_decision(self, html_content: str) -> List[Dict[str, str]]:
        """
        Processa HTML e extrai decisões

        Args:
            html_content: Conteúdo HTML da página

        Returns:
            Lista de decisões extraídas
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        decisions = []

        # Exemplo de parsing - adaptar conforme estrutura real do DJE
        articles = soup.find_all('article', class_='decision')
        for article in articles:
            try:
                decision = {
                    'title': article.find('h2').get_text(strip=True) if article.find('h2') else '',
                    'date': article.find('time').get('datetime', '') if article.find('time') else '',
                    'content': article.find('div', class_='content').get_text(strip=True) if article.find('div', class_='content') else '',
                    'url': article.find('a').get('href', '') if article.find('a') else '',
                    'collected_at': datetime.now().isoformat()
                }
                decisions.append(decision)
            except Exception as e:
                logger.warning(f"Erro ao processar decisão: {e}")
                continue

        return decisions

    def collect_decisions(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_pages: int = 10
    ) -> List[Dict[str, str]]:
        """
        Coleta decisões do DJE

        Args:
            start_date: Data inicial de coleta
            end_date: Data final de coleta
            max_pages: Número máximo de páginas a coletar

        Returns:
            Lista de decisões coletadas
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        logger.info(f"Coletando decisões de {start_date} até {end_date}")

        all_decisions = []

        for page in range(1, max_pages + 1):
            logger.info(f"Coletando página {page}/{max_pages}")

            # Construir URL com parâmetros (adaptar conforme API real)
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

    def save_decisions(self, decisions: List[Dict[str, str]], filename: Optional[str] = None):
        """
        Salva decisões em arquivo JSON

        Args:
            decisions: Lista de decisões
            filename: Nome do arquivo (opcional)
        """
        if not filename:
            filename = f"decisions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        output_path = settings.RAW_DATA_DIR / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(decisions, f, ensure_ascii=False, indent=2)

        logger.info(f"Salvas {len(decisions)} decisões em {output_path}")


def main():
    """Função principal para teste"""
    collector = DJECollector()
    decisions = collector.collect_decisions(max_pages=5)
    collector.save_decisions(decisions)
    logger.info(f"Coleta concluída: {len(decisions)} decisões")


if __name__ == "__main__":
    main()

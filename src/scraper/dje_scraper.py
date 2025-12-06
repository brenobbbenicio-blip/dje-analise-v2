"""
Scraper para coletar jurisprudência do TSE e TREs
"""
import time
import json
from typing import List, Dict, Optional
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from src.config import (
    DJE_BASE_URL,
    RAW_DATA_DIR,
    REQUEST_DELAY,
    MAX_DOCUMENTS_PER_SEARCH,
    TRE_CONFIGS,
    AVAILABLE_TRIBUNALS
)


class DJEScraper:
    """Scraper para coleta de jurisprudência eleitoral"""

    def __init__(self, tribunal: str = "TSE"):
        """
        Inicializa o scraper

        Args:
            tribunal: Código do tribunal (TSE, TRE-MG, TRE-RJ, TRE-PR, TRE-SC)
        """
        if tribunal not in AVAILABLE_TRIBUNALS:
            raise ValueError(
                f"Tribunal '{tribunal}' não disponível. "
                f"Opções: {', '.join(AVAILABLE_TRIBUNALS)}"
            )

        self.tribunal = tribunal
        self.tribunal_config = TRE_CONFIGS[tribunal]
        self.base_url = self.tribunal_config['url']

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_search_results(
        self,
        search_term: str,
        max_results: int = MAX_DOCUMENTS_PER_SEARCH
    ) -> List[Dict]:
        """
        Realiza busca e coleta resultados

        Args:
            search_term: Termo de busca
            max_results: Máximo de resultados

        Returns:
            Lista de documentos coletados
        """
        tribunal_name = self.tribunal_config['name']
        print(f"Buscando em {self.tribunal} - {tribunal_name}")
        print(f"Termo: '{search_term}'...")

        documents = []

        # Nota: Este é um exemplo simplificado
        # A implementação real dependeria da estrutura específica do site de cada tribunal
        # Por ora, criamos documentos de exemplo

        # Simulação de documentos (em produção, faria scraping real)
        example_docs = self._generate_example_documents(search_term, max_results)

        for doc in example_docs:
            # Adicionar informação do tribunal aos metadados
            doc['metadata']['tribunal'] = self.tribunal
            doc['metadata']['tribunal_name'] = tribunal_name
            doc['metadata']['state'] = self.tribunal_config['state']

            documents.append(doc)
            time.sleep(REQUEST_DELAY / 10)  # Delay menor para exemplos

        print(f"✅ Coletados {len(documents)} documentos de {self.tribunal}")
        return documents

    def _generate_example_documents(
        self,
        search_term: str,
        count: int
    ) -> List[Dict]:
        """
        Gera documentos de exemplo para demonstração

        Args:
            search_term: Termo de busca
            count: Número de documentos

        Returns:
            Lista de documentos de exemplo
        """
        # Obter documentos de exemplo do tribunal específico
        examples = TRE_EXAMPLE_DOCUMENTS.get(self.tribunal, [])

        if not examples:
            # Fallback para TSE se não houver exemplos
            examples = TRE_EXAMPLE_DOCUMENTS.get("TSE", [])

        # Criar cópias dos documentos para não modificar os originais
        result = []
        for i in range(min(count, len(examples))):
            doc_copy = {
                'title': examples[i]['title'],
                'text': examples[i]['text'],
                'metadata': examples[i]['metadata'].copy()
            }
            result.append(doc_copy)

        return result

    @staticmethod
    def scrape_all_tribunals(
        search_term: str,
        max_per_tribunal: int = 2,
        tribunals: Optional[List[str]] = None
    ) -> Dict[str, List[Dict]]:
        """
        Coleta documentos de múltiplos tribunais

        Args:
            search_term: Termo de busca
            max_per_tribunal: Máximo de documentos por tribunal
            tribunals: Lista de tribunais (None = todos)

        Returns:
            Dicionário com documentos por tribunal
        """
        if tribunals is None:
            tribunals = AVAILABLE_TRIBUNALS

        all_documents = {}

        for tribunal in tribunals:
            scraper = DJEScraper(tribunal=tribunal)
            docs = scraper.scrape_search_results(
                search_term=search_term,
                max_results=max_per_tribunal
            )
            all_documents[tribunal] = docs

        return all_documents

    def save_documents(self, documents: List[Dict], filename: str):
        """
        Salva documentos coletados

        Args:
            documents: Lista de documentos
            filename: Nome do arquivo
        """
        filepath = RAW_DATA_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)

        print(f"Salvos {len(documents)} documentos em {filepath}")

    def load_documents(self, filename: str) -> List[Dict]:
        """
        Carrega documentos salvos

        Args:
            filename: Nome do arquivo

        Returns:
            Lista de documentos
        """
        filepath = RAW_DATA_DIR / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            documents = json.load(f)

        return documents

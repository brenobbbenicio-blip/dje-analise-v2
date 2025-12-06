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
from src.scraper.html_parser import TSEParser, TREParser
from src.scraper.example_documents import TRE_EXAMPLE_DOCUMENTS


class DJEScraper:
    """Scraper para coleta de jurisprudência eleitoral"""

    def __init__(self, tribunal: str = "TSE", use_real_scraping: bool = False):
        """
        Inicializa o scraper

        Args:
            tribunal: Código do tribunal (TSE, TRE-MG, TRE-RJ, TRE-PR, TRE-SC, etc)
            use_real_scraping: Se True, tenta fazer raspagem real do site
        """
        if tribunal not in AVAILABLE_TRIBUNALS:
            raise ValueError(
                f"Tribunal '{tribunal}' não disponível. "
                f"Opções: {', '.join(AVAILABLE_TRIBUNALS)}"
            )

        self.tribunal = tribunal
        self.tribunal_config = TRE_CONFIGS[tribunal]
        self.base_url = self.tribunal_config['url']
        self.use_real_scraping = use_real_scraping

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
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

        # Tentar raspagem real se habilitado
        if self.use_real_scraping:
            try:
                print(f"🌐 Tentando raspagem real do site...")
                real_docs = self._scrape_real_website(search_term, max_results)
                if real_docs and len(real_docs) > 0:
                    documents = real_docs
                    print(f"✅ Raspagem real bem-sucedida!")
                else:
                    print(f"⚠️  Raspagem real não retornou resultados, usando exemplos...")
                    documents = self._generate_example_documents(search_term, max_results)
            except Exception as e:
                print(f"⚠️  Erro na raspagem real: {e}")
                print(f"📄 Usando documentos de exemplo como fallback...")
                documents = self._generate_example_documents(search_term, max_results)
        else:
            # Usar documentos de exemplo
            documents = self._generate_example_documents(search_term, max_results)

        # Adicionar informação do tribunal aos metadados
        for doc in documents:
            doc['metadata']['tribunal'] = self.tribunal
            doc['metadata']['tribunal_name'] = tribunal_name
            doc['metadata']['state'] = self.tribunal_config['state']
            time.sleep(REQUEST_DELAY / 10)  # Delay menor para exemplos

        print(f"✅ Coletados {len(documents)} documentos de {self.tribunal}")
        return documents

    def _scrape_real_website(
        self,
        search_term: str,
        max_results: int
    ) -> List[Dict]:
        """
        Faz raspagem real do site do tribunal

        Args:
            search_term: Termo de busca
            max_results: Máximo de resultados

        Returns:
            Lista de documentos raspados

        Raises:
            Exception: Em caso de erro na raspagem
        """
        documents = []

        # Obter padrões de URL específicos do tribunal
        search_patterns = self.tribunal_config.get('search_patterns', [
            "/busca?q={term}",
            "/jurisprudencia/busca?termo={term}",
            "/pesquisa?texto={term}",
            "?s={term}"
        ])

        # Construir URLs de busca usando os padrões do tribunal
        search_urls = [
            f"{self.base_url}{pattern.format(term=search_term)}"
            for pattern in search_patterns
        ]

        # Tentar cada padrão de URL
        for search_url in search_urls:
            try:
                print(f"   Tentando URL: {search_url[:50]}...")
                response = self.session.get(
                    search_url,
                    timeout=30,
                    allow_redirects=True
                )

                if response.status_code == 200:
                    # Usar parser apropriado
                    if self.tribunal == "TSE":
                        parsed_docs = TSEParser.parse_search_results(response.text)
                    else:
                        parsed_docs = TREParser.parse_search_results(response.text, self.tribunal)

                    if parsed_docs and len(parsed_docs) > 0:
                        documents.extend(parsed_docs[:max_results])
                        print(f"   ✓ Encontrados {len(parsed_docs)} resultados")
                        break  # URL funcionou, não precisa tentar outras

                time.sleep(REQUEST_DELAY)

            except requests.RequestException as e:
                # Continuar tentando outras URLs
                continue

        return documents[:max_results]

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

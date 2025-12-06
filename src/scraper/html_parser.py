"""
Parser HTML para extrair jurisprudência dos sites dos tribunais eleitorais
"""
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re


class TSEParser:
    """Parser para o site do TSE"""

    @staticmethod
    def parse_search_results(html_content: str) -> List[Dict]:
        """
        Extrai resultados de busca da página do TSE

        Args:
            html_content: HTML da página de resultados

        Returns:
            Lista de dicionários com dados dos acórdãos
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []

        # Tentar diferentes seletores comuns em sites de jurisprudência
        # Padrão 1: divs com classe 'resultado' ou 'jurisprudencia'
        items = soup.find_all(['div', 'article'], class_=re.compile(r'(resultado|jurisprudencia|acordao|decisao)', re.I))

        if not items:
            # Padrão 2: tabelas com resultados
            items = soup.find_all('tr', class_=re.compile(r'(linha|row|item)', re.I))

        if not items:
            # Padrão 3: listas
            items = soup.find_all('li', class_=re.compile(r'(resultado|item)', re.I))

        for item in items:
            doc = TSEParser._parse_item(item)
            if doc:
                results.append(doc)

        return results

    @staticmethod
    def _parse_item(item) -> Optional[Dict]:
        """
        Extrai dados de um item individual

        Args:
            item: Elemento BeautifulSoup

        Returns:
            Dicionário com dados do documento ou None
        """
        try:
            # Extrair título
            title_elem = item.find(['h2', 'h3', 'h4', 'strong', 'b'])
            title = title_elem.get_text(strip=True) if title_elem else "Acórdão TSE"

            # Extrair número do acórdão
            number_match = re.search(r'(?:Acórdão|Ac\.|AC)\s*(?:nº|n\.?|#)?\s*([\d\.\-/]+)',
                                    item.get_text(), re.I)
            number = number_match.group(1) if number_match else "S/N"

            # Extrair ano
            year_match = re.search(r'\b(20\d{2}|19\d{2})\b', item.get_text())
            year = int(year_match.group(1)) if year_match else 2024

            # Extrair texto completo
            # Remover elementos de navegação
            for nav in item.find_all(['nav', 'button', 'a'], class_=re.compile(r'(btn|link)', re.I)):
                nav.decompose()

            text = item.get_text(separator='\n', strip=True)

            # Limpar texto
            text = re.sub(r'\n+', '\n', text)
            text = re.sub(r'\s+', ' ', text)

            # Extrair ementa (geralmente em parágrafos ou divs específicas)
            ementa_elem = item.find(['p', 'div'], class_=re.compile(r'(ementa|resumo|texto)', re.I))
            ementa = ementa_elem.get_text(strip=True) if ementa_elem else text[:500]

            # Extrair tema/assunto
            tema_elem = item.find(['span', 'div'], class_=re.compile(r'(tema|assunto|categoria)', re.I))
            tema = tema_elem.get_text(strip=True) if tema_elem else "Direito Eleitoral"

            # Verificar se tem conteúdo válido
            if len(text) < 50:
                return None

            return {
                'title': title,
                'text': ementa if len(ementa) > 100 else text[:1000],
                'metadata': {
                    'number': number,
                    'year': year,
                    'type': 'Acórdão',
                    'tema': tema,
                    'source': 'TSE - Raspagem Real'
                }
            }
        except Exception as e:
            # Em caso de erro, retornar None
            return None

    @staticmethod
    def parse_detail_page(html_content: str) -> Optional[Dict]:
        """
        Extrai dados de uma página de detalhes de acórdão

        Args:
            html_content: HTML da página de detalhes

        Returns:
            Dicionário com dados completos do acórdão
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        try:
            # Extrair conteúdo principal
            main_content = soup.find(['div', 'article'], class_=re.compile(r'(conteudo|content|main|acordao)', re.I))

            if not main_content:
                main_content = soup.find(['div'], id=re.compile(r'(conteudo|content|main)', re.I))

            if not main_content:
                main_content = soup

            # Extrair texto completo
            for script in main_content.find_all(['script', 'style', 'nav', 'header', 'footer']):
                script.decompose()

            full_text = main_content.get_text(separator='\n', strip=True)

            # Limpar
            full_text = re.sub(r'\n{3,}', '\n\n', full_text)
            full_text = re.sub(r'[ \t]+', ' ', full_text)

            return {
                'text': full_text,
                'html': str(main_content)
            }
        except Exception:
            return None


class TREParser(TSEParser):
    """Parser para sites dos TREs (herda do TSE com pequenas adaptações)"""

    @staticmethod
    def parse_search_results(html_content: str, tribunal: str = "TRE") -> List[Dict]:
        """
        Extrai resultados de busca de um TRE

        Args:
            html_content: HTML da página
            tribunal: Código do tribunal (TRE-MG, etc)

        Returns:
            Lista de documentos
        """
        # Usa o parser do TSE como base
        results = TSEParser.parse_search_results(html_content)

        # Adiciona informação do tribunal
        for doc in results:
            doc['metadata']['source'] = f'{tribunal} - Raspagem Real'
            # Ajusta título se necessário
            if 'TSE' in doc['title'] and tribunal != 'TSE':
                doc['title'] = doc['title'].replace('TSE', tribunal)

        return results

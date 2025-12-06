"""
Modelos de dados para geração de peças processuais
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal
from datetime import datetime


@dataclass
class Party:
    """Representa uma parte processual"""
    name: str
    role: Literal["autor", "réu", "recorrente", "recorrido", "requerente", "requerido"]
    cpf_cnpj: Optional[str] = None
    address: Optional[str] = None
    lawyer: Optional[str] = None
    oab: Optional[str] = None


@dataclass
class LegalArgument:
    """Argumento jurídico com fundamentação"""
    title: str
    description: str
    legal_basis: List[str]  # Leis, artigos
    jurisprudence: List[Dict]  # Jurisprudências de apoio
    strength: Literal["fraco", "moderado", "forte", "muito_forte"]


@dataclass
class Citation:
    """Citação de jurisprudência ou legislação"""
    type: Literal["jurisprudencia", "lei", "doutrina"]
    source: str  # Nome da fonte (TSE, Lei 9.504/97, etc)
    text: str  # Texto da citação
    reference: str  # Referência completa formatada
    relevance: float = 0.0


@dataclass
class DocumentSection:
    """Seção de um documento processual"""
    title: str
    content: str
    subsections: List['DocumentSection'] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)


@dataclass
class LegalDocument:
    """Documento processual completo"""
    document_type: Literal[
        "petição_inicial",
        "recurso",
        "parecer",
        "contestação",
        "impugnação",
        "memoriale",
        "agravo"
    ]
    title: str
    tribunal: str
    process_number: Optional[str] = None

    # Partes
    parties: List[Party] = field(default_factory=list)

    # Estrutura
    sections: List[DocumentSection] = field(default_factory=list)

    # Argumentos
    arguments: List[LegalArgument] = field(default_factory=list)

    # Pedidos
    requests: List[str] = field(default_factory=list)

    # Metadados
    created_at: datetime = field(default_factory=datetime.now)
    generated_by_ai: bool = True

    def get_main_party(self, role: str) -> Optional[Party]:
        """Retorna a parte principal de um determinado papel"""
        for party in self.parties:
            if party.role == role:
                return party
        return None

    def add_section(self, title: str, content: str, citations: List[Citation] = None):
        """Adiciona uma seção ao documento"""
        section = DocumentSection(
            title=title,
            content=content,
            citations=citations or []
        )
        self.sections.append(section)

    def add_argument(self, argument: LegalArgument):
        """Adiciona um argumento jurídico"""
        self.arguments.append(argument)

    def add_request(self, request: str):
        """Adiciona um pedido"""
        self.requests.append(request)


@dataclass
class DocumentTemplate:
    """Template para geração de documentos"""
    name: str
    document_type: str
    description: str
    required_sections: List[str]
    optional_sections: List[str] = field(default_factory=list)

    # Prompts para IA
    structure_prompt: str = ""
    content_prompts: Dict[str, str] = field(default_factory=dict)


@dataclass
class GenerationRequest:
    """Requisição para geração de documento"""
    document_type: str
    tribunal: str

    # Contexto do caso
    case_description: str
    objective: str  # O que se pretende com a peça

    # Partes
    parties: List[Party] = field(default_factory=list)

    # Teses e argumentos desejados
    main_arguments: List[str] = field(default_factory=list)

    # Configurações
    tone: Literal["formal", "muito_formal", "técnico"] = "formal"
    max_jurisprudence: int = 5
    include_doctrine: bool = False

    # Filtros de busca
    tribunal_filter: Optional[List[str]] = None
    year_filter: Optional[int] = None


@dataclass
class GenerationResult:
    """Resultado da geração de documento"""
    document: LegalDocument
    formatted_text: str  # Texto formatado pronto para uso

    # Estatísticas
    word_count: int = 0
    jurisprudence_count: int = 0
    argument_count: int = 0

    # Qualidade
    quality_score: float = 0.0  # 0.0 a 1.0
    suggestions: List[str] = field(default_factory=list)

    # Arquivos gerados
    generated_files: Dict[str, str] = field(default_factory=dict)

    def export_to_docx(self, filepath: str):
        """Exporta para arquivo DOCX (placeholder)"""
        # TODO: Implementar exportação DOCX
        pass

    def export_to_pdf(self, filepath: str):
        """Exporta para PDF (placeholder)"""
        # TODO: Implementar exportação PDF
        pass

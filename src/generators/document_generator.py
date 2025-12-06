"""
Gerador Automático de Peças Processuais com IA
Gera petições, recursos e pareceres fundamentados em jurisprudência
"""
import openai
from typing import List, Dict, Optional
from chromadb.api.models.Collection import Collection

from ..models.document_models import (
    LegalDocument,
    DocumentSection,
    Citation,
    LegalArgument,
    Party,
    GenerationRequest,
    GenerationResult
)
from ..models import RAGSystem
from ..config import OPENAI_API_KEY, CHAT_MODEL
from .document_templates import DocumentTemplates


class DocumentGenerator:
    """
    Gerador automático de peças processuais
    Usa IA + RAG para gerar documentos fundamentados
    """

    def __init__(self, rag_system: Optional[RAGSystem] = None):
        """
        Inicializa o gerador

        Args:
            rag_system: Sistema RAG para busca de jurisprudência (opcional)
        """
        self.rag = rag_system or RAGSystem()
        openai.api_key = OPENAI_API_KEY
        self.templates = DocumentTemplates()

    def generate_document(
        self,
        request: GenerationRequest
    ) -> GenerationResult:
        """
        Gera documento processual completo

        Args:
            request: Requisição de geração

        Returns:
            Resultado com documento gerado e formatado
        """
        print(f"\n🤖 Gerando {request.document_type}...")
        print(f"   Tribunal: {request.tribunal}")
        print(f"   Objetivo: {request.objective[:80]}...")

        # 1. Obter template
        template = self.templates.get_template(request.document_type)
        print(f"\n📋 Template: {template.name}")

        # 2. Buscar jurisprudência relevante
        jurisprudence = self._search_jurisprudence(request)
        print(f"⚖️  Jurisprudência encontrada: {len(jurisprudence)} precedentes")

        # 3. Gerar argumentos jurídicos
        arguments = self._generate_arguments(request, jurisprudence)
        print(f"💡 Argumentos gerados: {len(arguments)}")

        # 4. Criar documento base
        document = LegalDocument(
            document_type=request.document_type,
            title=self._generate_title(request),
            tribunal=request.tribunal,
            parties=request.parties,
            arguments=arguments
        )

        # 5. Gerar seções do documento
        self._generate_sections(document, request, template, jurisprudence)
        print(f"📄 Seções geradas: {len(document.sections)}")

        # 6. Gerar pedidos
        self._generate_requests(document, request)
        print(f"✅ Pedidos formulados: {len(document.requests)}")

        # 7. Formatar documento
        formatted_text = self._format_document(document, request)

        # 8. Calcular estatísticas e qualidade
        stats = self._calculate_statistics(document, formatted_text)

        # 9. Criar resultado
        result = GenerationResult(
            document=document,
            formatted_text=formatted_text,
            word_count=stats['word_count'],
            jurisprudence_count=stats['jurisprudence_count'],
            argument_count=len(arguments),
            quality_score=self._assess_quality(document),
            suggestions=self._generate_suggestions(document)
        )

        print(f"\n✅ Documento gerado com sucesso!")
        print(f"   Palavras: {result.word_count}")
        print(f"   Qualidade: {result.quality_score:.1%}")

        return result

    def _search_jurisprudence(
        self,
        request: GenerationRequest
    ) -> List[Dict]:
        """Busca jurisprudência relevante usando RAG"""
        # Construir query de busca
        search_query = f"{request.case_description} {request.objective}"

        # Buscar no RAG
        rag_result = self.rag.query(
            question=search_query,
            tribunal_filter=request.tribunal_filter[0] if request.tribunal_filter else None,
            n_results=request.max_jurisprudence
        )

        # Converter para formato de citações
        jurisprudence = []
        if 'sources' in rag_result:
            for source in rag_result['sources']:
                jurisprudence.append({
                    'title': source.get('title', ''),
                    'text': source.get('text', ''),
                    'tribunal': source.get('tribunal', ''),
                    'number': source.get('number', ''),
                    'year': source.get('year', ''),
                    'relevance': source.get('relevance', 0.0)
                })

        return jurisprudence

    def _generate_arguments(
        self,
        request: GenerationRequest,
        jurisprudence: List[Dict]
    ) -> List[LegalArgument]:
        """Gera argumentos jurídicos com base na jurisprudência"""
        arguments = []

        # Para cada argumento principal sugerido
        for arg_description in request.main_arguments:
            # Buscar jurisprudência específica para este argumento
            relevant_juris = self._filter_relevant_jurisprudence(
                arg_description,
                jurisprudence
            )

            # Gerar argumento com IA
            argument = self._ai_generate_argument(
                arg_description,
                relevant_juris,
                request
            )

            arguments.append(argument)

        return arguments

    def _ai_generate_argument(
        self,
        description: str,
        jurisprudence: List[Dict],
        request: GenerationRequest
    ) -> LegalArgument:
        """Usa IA para gerar um argumento jurídico estruturado"""
        # Preparar contexto de jurisprudência
        juris_context = "\n\n".join([
            f"- {j['title']}: {j['text'][:200]}..."
            for j in jurisprudence[:3]
        ])

        prompt = f"""Você é um advogado especialista em direito eleitoral. Crie um argumento jurídico estruturado.

ARGUMENTO: {description}
OBJETIVO: {request.objective}
CONTEXTO: {request.case_description}

JURISPRUDÊNCIA DISPONÍVEL:
{juris_context}

Crie um argumento jurídico em formato JSON:
{{
  "title": "Título do argumento",
  "description": "Desenvolvimento do argumento (2-3 parágrafos, linguagem jurídica formal)",
  "legal_basis": ["Lei/artigo 1", "Lei/artigo 2"],
  "strength": "fraco|moderado|forte|muito_forte"
}}

O argumento deve ser tecnicamente sólido, bem fundamentado e persuasivo."""

        try:
            response = openai.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um advogado especialista em direito eleitoral brasileiro."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                response_format={"type": "json_object"}
            )

            import json
            arg_data = json.loads(response.choices[0].message.content)

            return LegalArgument(
                title=arg_data.get('title', description),
                description=arg_data.get('description', ''),
                legal_basis=arg_data.get('legal_basis', []),
                jurisprudence=jurisprudence,
                strength=arg_data.get('strength', 'moderado')
            )

        except Exception as e:
            print(f"⚠️  Erro ao gerar argumento: {e}")
            # Fallback: argumento básico
            return LegalArgument(
                title=description,
                description=f"Argumento relativo a {description}",
                legal_basis=["Constituição Federal, art. 14"],
                jurisprudence=jurisprudence,
                strength="moderado"
            )

    def _filter_relevant_jurisprudence(
        self,
        argument: str,
        jurisprudence: List[Dict]
    ) -> List[Dict]:
        """Filtra jurisprudência relevante para um argumento específico"""
        # Implementação simples: retorna jurisprudências que mencionam termos-chave
        keywords = argument.lower().split()
        relevant = []

        for juris in jurisprudence:
            text = juris.get('text', '').lower()
            if any(kw in text for kw in keywords if len(kw) > 4):
                relevant.append(juris)

        return relevant[:3]  # Máximo 3 por argumento

    def _generate_sections(
        self,
        document: LegalDocument,
        request: GenerationRequest,
        template,
        jurisprudence: List[Dict]
    ):
        """Gera seções do documento usando IA"""
        # Seções obrigatórias
        for section_name in template.required_sections:
            content = self._ai_generate_section(
                section_name,
                request,
                template,
                document.arguments,
                jurisprudence
            )

            citations = self._extract_citations_for_section(
                section_name,
                jurisprudence
            )

            document.add_section(
                title=self._format_section_title(section_name),
                content=content,
                citations=citations
            )

    def _ai_generate_section(
        self,
        section_name: str,
        request: GenerationRequest,
        template,
        arguments: List[LegalArgument],
        jurisprudence: List[Dict]
    ) -> str:
        """Gera conteúdo de uma seção usando IA"""
        # Obter prompt específico da seção
        section_prompt = template.content_prompts.get(
            section_name,
            f"Redija a seção {section_name} de forma técnica e objetiva."
        )

        # Contexto de argumentos
        args_context = "\n".join([
            f"- {arg.title}: {arg.description[:150]}..."
            for arg in arguments
        ])

        # Contexto de jurisprudência
        juris_context = "\n".join([
            f"- {j.get('tribunal', 'N/A')} - {j.get('title', 'Acórdão')}"
            for j in jurisprudence[:5]
        ])

        prompt = f"""Você é um advogado especialista. Redija a seção "{section_name}" de um(a) {request.document_type}.

ORIENTAÇÕES:
{section_prompt}

CONTEXTO DO CASO:
{request.case_description}

OBJETIVO:
{request.objective}

ARGUMENTOS PRINCIPAIS:
{args_context}

JURISPRUDÊNCIA DISPONÍVEL:
{juris_context}

TOM: {request.tone}

Redija o texto da seção de forma profissional, técnica e persuasiva. Use linguagem jurídica adequada.
Não inclua o título da seção, apenas o conteúdo."""

        try:
            response = openai.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um advogado experiente em direito eleitoral."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"⚠️  Erro ao gerar seção {section_name}: {e}")
            return f"[Seção {section_name} - conteúdo a ser desenvolvido]"

    def _generate_requests(
        self,
        document: LegalDocument,
        request: GenerationRequest
    ):
        """Gera pedidos processuais usando IA"""
        prompt = f"""Formule os pedidos processuais para um(a) {request.document_type} eleitoral.

OBJETIVO: {request.objective}
ARGUMENTOS: {len(document.arguments)} argumentos desenvolvidos

Gere uma lista de pedidos em formato JSON:
{{
  "pedidos": [
    "Pedido principal específico",
    "Pedido subsidiário (se houver)",
    "Pedidos acessórios (provas, tutela, etc)"
  ]
}}

Os pedidos devem ser:
- Claros e específicos
- Juridicamente viáveis
- Alinhados com o objetivo
- Em ordem de prioridade"""

        try:
            response = openai.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um advogado formulando pedidos processuais."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)

            for pedido in result.get('pedidos', []):
                document.add_request(pedido)

        except Exception as e:
            print(f"⚠️  Erro ao gerar pedidos: {e}")
            # Fallback
            document.add_request(f"Requer o deferimento do presente {request.document_type}")

    def _format_section_title(self, section_name: str) -> str:
        """Formata título de seção"""
        return section_name.upper().replace("_", " ")

    def _extract_citations_for_section(
        self,
        section_name: str,
        jurisprudence: List[Dict]
    ) -> List[Citation]:
        """Extrai citações relevantes para uma seção"""
        citations = []

        # Para seção de direito, incluir jurisprudência
        if "direito" in section_name.lower() or "fundamento" in section_name.lower():
            for juris in jurisprudence[:3]:
                citation = Citation(
                    type="jurisprudencia",
                    source=f"{juris.get('tribunal', 'TSE')} - Acórdão {juris.get('number', 'N/A')}",
                    text=juris.get('text', '')[:200] + "...",
                    reference=self._format_citation_reference(juris),
                    relevance=juris.get('relevance', 0.0)
                )
                citations.append(citation)

        return citations

    def _format_citation_reference(self, juris: Dict) -> str:
        """Formata referência de citação"""
        tribunal = juris.get('tribunal', 'TSE')
        number = juris.get('number', 'N/A')
        year = juris.get('year', '')

        return f"{tribunal}, Acórdão nº {number}, {year}."

    def _format_document(
        self,
        document: LegalDocument,
        request: GenerationRequest
    ) -> str:
        """Formata documento completo para texto"""
        lines = []

        # Cabeçalho
        lines.append(f"EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DO {document.tribunal.upper()}")
        lines.append("")
        lines.append("")

        # Identificação das partes
        for party in document.parties:
            lines.append(self._format_party(party))
        lines.append("")

        # Título do documento
        lines.append(document.title.upper())
        lines.append("=" * 80)
        lines.append("")

        # Seções
        for section in document.sections:
            lines.append(section.title)
            lines.append("-" * 80)
            lines.append("")
            lines.append(section.content)
            lines.append("")

            # Citações
            if section.citations:
                lines.append("Jurisprudência:")
                for i, citation in enumerate(section.citations, 1):
                    lines.append(f"  {i}. {citation.reference}")
                lines.append("")

        # Argumentos
        if document.arguments:
            lines.append("DOS ARGUMENTOS JURÍDICOS")
            lines.append("-" * 80)
            lines.append("")

            for i, arg in enumerate(document.arguments, 1):
                lines.append(f"{i}. {arg.title}")
                lines.append("")
                lines.append(arg.description)
                lines.append("")

                if arg.legal_basis:
                    lines.append("Base legal:")
                    for base in arg.legal_basis:
                        lines.append(f"  - {base}")
                    lines.append("")

        # Pedidos
        lines.append("DOS PEDIDOS")
        lines.append("-" * 80)
        lines.append("")
        lines.append("Diante do exposto, requer:")
        lines.append("")

        for i, req in enumerate(document.requests, 1):
            lines.append(f"  {i}) {req};")

        lines.append("")
        lines.append("Nestes termos, pede deferimento.")
        lines.append("")
        lines.append("")

        # Encerramento
        lines.append(f"Local, {document.created_at.strftime('%d de %B de %Y')}.")
        lines.append("")
        lines.append("")

        # Assinatura
        main_lawyer = next(
            (p.lawyer for p in document.parties if p.lawyer),
            "Advogado(a)"
        )
        main_oab = next(
            (p.oab for p in document.parties if p.oab),
            "OAB/UF 000.000"
        )

        lines.append("_" * 40)
        lines.append(main_lawyer)
        lines.append(main_oab)

        return "\n".join(lines)

    def _format_party(self, party: Party) -> str:
        """Formata identificação de parte"""
        role_labels = {
            "autor": "Autor(a)",
            "réu": "Réu/Ré",
            "recorrente": "Recorrente",
            "recorrido": "Recorrido(a)",
            "requerente": "Requerente",
            "requerido": "Requerido(a)"
        }

        label = role_labels.get(party.role, party.role.title())
        text = f"{label}: {party.name}"

        if party.cpf_cnpj:
            text += f", CPF/CNPJ: {party.cpf_cnpj}"

        if party.address:
            text += f", {party.address}"

        if party.lawyer:
            text += f", advogado: {party.lawyer}"
            if party.oab:
                text += f" ({party.oab})"

        return text

    def _generate_title(self, request: GenerationRequest) -> str:
        """Gera título do documento"""
        type_labels = {
            "petição_inicial": "PETIÇÃO INICIAL",
            "recurso": "RECURSO ELEITORAL",
            "parecer": "PARECER TÉCNICO-JURÍDICO",
            "impugnação": "IMPUGNAÇÃO DE REGISTRO DE CANDIDATURA",
            "contestação": "CONTESTAÇÃO"
        }

        return type_labels.get(request.document_type, request.document_type.upper())

    def _calculate_statistics(
        self,
        document: LegalDocument,
        text: str
    ) -> Dict:
        """Calcula estatísticas do documento"""
        word_count = len(text.split())
        juris_count = sum(len(s.citations) for s in document.sections)

        return {
            'word_count': word_count,
            'jurisprudence_count': juris_count
        }

    def _assess_quality(self, document: LegalDocument) -> float:
        """Avalia qualidade do documento (0.0 a 1.0)"""
        score = 0.0

        # Tem seções? +0.2
        if len(document.sections) >= 3:
            score += 0.2

        # Tem argumentos? +0.2
        if len(document.arguments) >= 2:
            score += 0.2

        # Tem pedidos? +0.2
        if len(document.requests) >= 1:
            score += 0.2

        # Tem jurisprudência? +0.2
        total_citations = sum(len(s.citations) for s in document.sections)
        if total_citations >= 2:
            score += 0.2

        # Tem partes identificadas? +0.2
        if len(document.parties) >= 1:
            score += 0.2

        return min(1.0, score)

    def _generate_suggestions(self, document: LegalDocument) -> List[str]:
        """Gera sugestões de melhoria"""
        suggestions = []

        # Verificar jurisprudência
        total_citations = sum(len(s.citations) for s in document.sections)
        if total_citations < 3:
            suggestions.append("Considere adicionar mais jurisprudência para fortalecer os argumentos")

        # Verificar argumentos
        if len(document.arguments) < 2:
            suggestions.append("Desenvolva mais argumentos jurídicos para robustecer a peça")

        # Verificar pedidos
        if len(document.requests) < 2:
            suggestions.append("Considere adicionar pedidos subsidiários ou acessórios")

        # Verificar argumentos fortes
        strong_args = [a for a in document.arguments if a.strength in ["forte", "muito_forte"]]
        if not strong_args:
            suggestions.append("Tente desenvolver argumentos mais robustos com jurisprudência consolidada")

        return suggestions

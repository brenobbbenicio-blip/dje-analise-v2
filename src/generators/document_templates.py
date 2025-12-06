"""
Templates para geração de peças processuais eleitorais
"""
from typing import Dict
from ..models.document_models import DocumentTemplate


class DocumentTemplates:
    """Biblioteca de templates de documentos processuais"""

    @staticmethod
    def get_all_templates() -> Dict[str, DocumentTemplate]:
        """Retorna todos os templates disponíveis"""
        return {
            "petição_inicial": DocumentTemplates.peticao_inicial(),
            "recurso": DocumentTemplates.recurso_eleitoral(),
            "parecer": DocumentTemplates.parecer_tecnico(),
            "impugnação": DocumentTemplates.impugnacao_registro(),
            "contestação": DocumentTemplates.contestacao(),
        }

    @staticmethod
    def peticao_inicial() -> DocumentTemplate:
        """Template para petição inicial"""
        return DocumentTemplate(
            name="Petição Inicial",
            document_type="petição_inicial",
            description="Petição inicial para ações eleitorais",
            required_sections=[
                "cabeçalho",
                "qualificação_partes",
                "dos_fatos",
                "do_direito",
                "dos_pedidos"
            ],
            optional_sections=[
                "das_provas",
                "do_valor_causa",
                "requerimentos_finais"
            ],
            structure_prompt="""
Estruture uma petição inicial eleitoral seguindo a ordem:
1. Identificação do tribunal e comarca
2. Qualificação completa das partes
3. Exposição dos fatos de forma cronológica e objetiva
4. Fundamentação jurídica com base em leis e jurisprudência
5. Formulação clara dos pedidos
6. Requerimento de provas
7. Valor da causa (se aplicável)
8. Encerramento formal
""",
            content_prompts={
                "dos_fatos": """
Redija a seção DOS FATOS de forma:
- Cronológica e objetiva
- Com linguagem jurídica formal
- Destacando os fatos juridicamente relevantes
- Sem adjetivações desnecessárias
- Incluindo datas, locais e documentos quando relevante
""",
                "do_direito": """
Redija a seção DO DIREITO com:
- Fundamentação legal completa (artigos, leis, resoluções)
- Jurisprudência do TSE e TREs pertinente
- Doutrina quando aplicável
- Argumentação lógica e encadeada
- Demonstração do direito alegado
- Citações formatadas corretamente
""",
                "dos_pedidos": """
Redija os pedidos de forma:
- Clara e específica
- Um pedido por item numerado
- Começando pelo pedido principal
- Incluindo pedidos subsidiários se houver
- Finalizando com "requer deferimento"
"""
            }
        )

    @staticmethod
    def recurso_eleitoral() -> DocumentTemplate:
        """Template para recurso eleitoral"""
        return DocumentTemplate(
            name="Recurso Eleitoral",
            document_type="recurso",
            description="Recurso contra decisão eleitoral",
            required_sections=[
                "cabeçalho",
                "qualificação_recorrente",
                "da_decisão_recorrida",
                "dos_fundamentos",
                "do_pedido"
            ],
            optional_sections=[
                "da_tempestividade",
                "do_cabimento",
                "dos_efeitos",
                "jurisprudência_favorável"
            ],
            structure_prompt="""
Estruture um recurso eleitoral seguindo:
1. Identificação do processo e decisão recorrida
2. Qualificação do recorrente
3. Demonstração de tempestividade e cabimento
4. Síntese da decisão recorrida
5. Fundamentos do recurso (razões de reforma)
6. Jurisprudência e doutrina de apoio
7. Pedido de reforma/anulação
8. Requerimentos processuais (efeito suspensivo, etc)
""",
            content_prompts={
                "da_decisão_recorrida": """
Redija resumo da decisão recorrida incluindo:
- Data da decisão
- Dispositivo principal
- Fundamentos utilizados
- Pontos que serão contestados
- De forma objetiva e imparcial
""",
                "dos_fundamentos": """
Redija os fundamentos do recurso:
- Demonstrando error in judicando ou in procedendo
- Com base em jurisprudência pacífica
- Citando precedentes favoráveis
- Argumentação técnica e robusta
- Contrapondo especificamente a decisão recorrida
""",
                "do_pedido": """
Formule pedido recursal:
- Solicitando provimento do recurso
- Especificando a reforma pretendida
- Indicando efeitos desejados (suspensivo, etc)
- De forma clara e objetiva
"""
            }
        )

    @staticmethod
    def parecer_tecnico() -> DocumentTemplate:
        """Template para parecer técnico"""
        return DocumentTemplate(
            name="Parecer Técnico-Jurídico",
            document_type="parecer",
            description="Parecer técnico sobre questão eleitoral",
            required_sections=[
                "consulta",
                "análise_fática",
                "análise_jurídica",
                "conclusão"
            ],
            optional_sections=[
                "jurisprudência_aplicável",
                "doutrina",
                "legislação_pertinente"
            ],
            structure_prompt="""
Estruture um parecer técnico-jurídico:
1. Apresentação da consulta/questão
2. Delimitação do objeto
3. Análise dos fatos apresentados
4. Análise jurídica fundamentada
5. Jurisprudência aplicável
6. Conclusão objetiva
7. Assinatura do parecerista
""",
            content_prompts={
                "análise_jurídica": """
Redija análise jurídica completa:
- Identificando as normas aplicáveis
- Interpretando dispositivos legais
- Citando jurisprudência consolidada
- Apresentando diferentes correntes (se houver)
- Com raciocínio técnico-jurídico
- Linguagem formal e precisa
""",
                "conclusão": """
Redija conclusão do parecer:
- Respondendo objetivamente à consulta
- Com base na análise realizada
- De forma fundamentada
- Clara e direta
- Sem ambiguidades
"""
            }
        )

    @staticmethod
    def impugnacao_registro() -> DocumentTemplate:
        """Template para impugnação de registro de candidatura"""
        return DocumentTemplate(
            name="Impugnação de Registro de Candidatura",
            document_type="impugnação",
            description="Impugnação de registro de candidato",
            required_sections=[
                "cabeçalho",
                "qualificação_impugnante",
                "do_candidato_impugnado",
                "dos_fundamentos",
                "das_inelegibilidades",
                "dos_pedidos"
            ],
            optional_sections=[
                "das_provas",
                "da_urgência",
                "jurisprudência"
            ],
            structure_prompt="""
Estruture impugnação de registro:
1. Identificação do processo de registro
2. Qualificação do impugnante
3. Identificação do candidato impugnado
4. Exposição dos fatos que motivam a impugnação
5. Demonstração de inelegibilidades (LC 64/90)
6. Fundamentação jurídica robusta
7. Rol de provas
8. Pedido de indeferimento do registro
""",
            content_prompts={
                "das_inelegibilidades": """
Redija sobre inelegibilidades:
- Identificando qual(is) hipótese(s) da LC 64/90
- Demonstrando o preenchimento dos requisitos
- Com jurisprudência específica do TSE
- Citando precedentes de casos similares
- Fundamentação técnica sólida
""",
                "dos_fundamentos": """
Fundamente a impugnação com:
- Fatos concretos e demonstráveis
- Base legal específica
- Jurisprudência consolidada
- Demonstração inequívoca
- Linguagem técnica e objetiva
"""
            }
        )

    @staticmethod
    def contestacao() -> DocumentTemplate:
        """Template para contestação"""
        return DocumentTemplate(
            name="Contestação",
            document_type="contestação",
            description="Contestação em processo eleitoral",
            required_sections=[
                "cabeçalho",
                "qualificação_contestante",
                "preliminares",
                "impugnação_aos_fatos",
                "do_direito",
                "dos_pedidos"
            ],
            optional_sections=[
                "das_provas",
                "reconvenção"
            ],
            structure_prompt="""
Estruture contestação:
1. Identificação do processo
2. Qualificação do contestante
3. Preliminares (se houver)
4. Impugnação específica aos fatos alegados
5. Fundamentação jurídica
6. Demonstração do descabimento da inicial
7. Provas
8. Pedido de improcedência
""",
            content_prompts={
                "impugnação_aos_fatos": """
Impugne os fatos alegados:
- Ponto por ponto da inicial
- Com provas ou indícios do contrário
- Demonstrando inconsistências
- De forma específica e fundamentada
- Sem admitir fatos prejudiciais
""",
                "preliminares": """
Redija preliminares (se aplicável):
- Ilegitimidade de parte
- Incompetência do juízo
- Inépcia da inicial
- Litispendência
- Outras matérias processuais
- De forma técnica e fundamentada
"""
            }
        )

    @staticmethod
    def get_template(document_type: str) -> DocumentTemplate:
        """
        Obtém template por tipo de documento

        Args:
            document_type: Tipo do documento

        Returns:
            Template correspondente

        Raises:
            ValueError: Se tipo não existir
        """
        templates = DocumentTemplates.get_all_templates()

        if document_type not in templates:
            available = ", ".join(templates.keys())
            raise ValueError(
                f"Template '{document_type}' não encontrado. "
                f"Disponíveis: {available}"
            )

        return templates[document_type]

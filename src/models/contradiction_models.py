"""
Modelos de dados para o sistema de detecção de contradições jurisprudenciais
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal
from datetime import datetime


@dataclass
class JurisprudenceCase:
    """Representa um caso jurisprudencial individual"""
    id: str
    title: str
    text: str
    tribunal: str
    tribunal_name: str
    number: Optional[str] = None
    year: Optional[int] = None
    decision_type: Optional[str] = None  # "provido", "não provido", "procedente", "improcedente", etc.
    tema: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class SimilarCase:
    """Par de casos similares para comparação"""
    case1: JurisprudenceCase
    case2: JurisprudenceCase
    similarity_score: float  # 0.0 a 1.0
    semantic_distance: float  # Distância no espaço vetorial


@dataclass
class Contradiction:
    """Representa uma contradição detectada entre jurisprudências"""
    id: str
    case1: JurisprudenceCase
    case2: JurisprudenceCase
    similarity_score: float
    contradiction_type: Literal[
        "decisao_oposta",      # Decisões opostas (provido vs não provido)
        "fundamento_diverso",   # Mesmo resultado, fundamentos contraditórios
        "interpretacao_divergente",  # Interpretações diferentes da lei
        "criterio_conflitante"  # Critérios de julgamento conflitantes
    ]
    contradiction_severity: Literal["baixa", "média", "alta", "crítica"]
    explanation: str  # Explicação da contradição gerada por IA
    legal_impact: str  # Impacto jurídico da contradição
    recommended_action: str  # Recomendação estratégica
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class ContradictionCluster:
    """Grupo de contradições relacionadas ao mesmo tema"""
    theme: str
    contradictions: List[Contradiction]
    affected_tribunals: List[str]
    total_cases: int
    severity_distribution: Dict[str, int]  # Contagem por nível de gravidade
    summary: str


@dataclass
class ContradictionReport:
    """Relatório completo de análise de contradições"""
    generated_at: datetime
    query: str
    total_cases_analyzed: int
    contradictions_found: int
    clusters: List[ContradictionCluster]
    tribunal_comparison: Dict[str, Dict]  # Estatísticas por tribunal
    highlights: List[str]  # Principais descobertas
    recommendations: List[str]  # Recomendações estratégicas

    def to_dict(self) -> Dict:
        """Converte relatório para dicionário"""
        return {
            'generated_at': self.generated_at.isoformat(),
            'query': self.query,
            'total_cases_analyzed': self.total_cases_analyzed,
            'contradictions_found': self.contradictions_found,
            'clusters': len(self.clusters),
            'tribunal_comparison': self.tribunal_comparison,
            'highlights': self.highlights,
            'recommendations': self.recommendations
        }

    def get_critical_contradictions(self) -> List[Contradiction]:
        """Retorna apenas contradições críticas"""
        critical = []
        for cluster in self.clusters:
            critical.extend([
                c for c in cluster.contradictions
                if c.contradiction_severity == "crítica"
            ])
        return critical

    def get_by_tribunal(self, tribunal: str) -> List[Contradiction]:
        """Retorna contradições envolvendo um tribunal específico"""
        result = []
        for cluster in self.clusters:
            result.extend([
                c for c in cluster.contradictions
                if c.case1.tribunal == tribunal or c.case2.tribunal == tribunal
            ])
        return result


@dataclass
class ContradictionAlert:
    """Alerta de contradição para notificação"""
    contradiction: Contradiction
    priority: Literal["baixa", "média", "alta", "urgente"]
    message: str
    actionable: bool
    tribunals_involved: List[str]
    created_at: datetime = field(default_factory=datetime.now)

    def format_alert(self) -> str:
        """Formata alerta para exibição"""
        emoji = {
            "baixa": "ℹ️",
            "média": "⚠️",
            "alta": "🔴",
            "urgente": "🚨"
        }

        return f"""
{emoji[self.priority]} ALERTA DE CONTRADIÇÃO - Prioridade {self.priority.upper()}

Tribunais: {' vs '.join(self.tribunais_involved)}
Tipo: {self.contradiction.contradiction_type}
Gravidade: {self.contradiction.contradiction_severity}

{self.message}

📋 Caso 1: {self.contradiction.case1.title}
   Tribunal: {self.contradiction.case1.tribunal_name}

📋 Caso 2: {self.contradiction.case2.title}
   Tribunal: {self.contradiction.case2.tribunal_name}

💡 Recomendação: {self.contradiction.recommended_action}

Similaridade: {self.contradiction.similarity_score:.2%}
Data: {self.created_at.strftime('%d/%m/%Y %H:%M')}
"""

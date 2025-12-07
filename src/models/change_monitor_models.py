"""
Modelos de dados para monitoramento de mudanças de entendimento jurisprudencial
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal
from datetime import datetime


@dataclass
class JurisprudenceSnapshot:
    """Snapshot de jurisprudência em um ponto temporal"""
    date: datetime
    tribunal: str
    theme: str
    decision_pattern: str  # "favorável", "desfavorável", "neutro"
    cases: List[Dict]
    total_cases: int
    favorable_ratio: float  # 0.0 a 1.0


@dataclass
class TrendPoint:
    """Ponto em uma tendência temporal"""
    date: datetime
    favorable_ratio: float
    total_cases: int
    representative_case: Optional[Dict] = None


@dataclass
class ChangeDetection:
    """Mudança detectada no entendimento"""
    id: str
    tribunal: str
    theme: str
    change_type: Literal[
        "inversão_total",      # De favorável para desfavorável ou vice-versa
        "endurecimento",       # Tornando-se mais restritivo
        "flexibilização",      # Tornando-se mais permissivo
        "consolidação",        # Posicionamento se consolidando
        "divergência"          # Aumentando divergência interna
    ]
    severity: Literal["baixa", "média", "alta", "crítica"]

    # Dados antes da mudança
    before_period: str
    before_ratio: float
    before_cases: int

    # Dados depois da mudança
    after_period: str
    after_ratio: float
    after_cases: int

    # Análise
    change_magnitude: float  # 0.0 a 1.0
    confidence: float  # 0.0 a 1.0
    detected_at: datetime
    explanation: str
    impact_assessment: str
    recommended_action: str

    # Casos chave
    landmark_cases: List[Dict] = field(default_factory=list)


@dataclass
class TrendAnalysis:
    """Análise de tendência temporal"""
    tribunal: str
    theme: str
    period_start: datetime
    period_end: datetime

    trend_points: List[TrendPoint]

    # Métricas
    overall_trend: Literal["crescente", "decrescente", "estável", "volátil"]
    trend_strength: float  # 0.0 a 1.0
    volatility: float  # 0.0 a 1.0

    # Estatísticas
    average_favorable_ratio: float
    max_favorable_ratio: float
    min_favorable_ratio: float
    total_cases_analyzed: int

    # Predição
    predicted_direction: Optional[str] = None
    prediction_confidence: Optional[float] = None


@dataclass
class MonitoringAlert:
    """Alerta de mudança de entendimento"""
    id: str
    change: ChangeDetection
    priority: Literal["baixa", "média", "alta", "urgente"]
    alert_type: Literal["mudança_detectada", "tendência_consolidada", "risco_mudança"]

    title: str
    message: str
    actionable: bool

    # Contexto
    affected_areas: List[str]  # Áreas do direito afetadas
    suggested_strategies: List[str]

    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    def format_alert(self) -> str:
        """Formata alerta para exibição"""
        emoji = {
            "baixa": "ℹ️",
            "média": "⚠️",
            "alta": "🔴",
            "urgente": "🚨"
        }

        type_emoji = {
            "mudança_detectada": "🔄",
            "tendência_consolidada": "📈",
            "risco_mudança": "⚠️"
        }

        lines = [
            f"{emoji[self.priority]} {type_emoji[self.alert_type]} {self.title.upper()}",
            "=" * 80,
            f"Prioridade: {self.priority.upper()}",
            f"Tribunal: {self.change.tribunal}",
            f"Tema: {self.change.theme}",
            f"Tipo: {self.change.change_type}",
            "",
            "MUDANÇA DETECTADA:",
            f"  Antes ({self.change.before_period}): {self.change.before_ratio:.1%} favorável ({self.change.before_cases} casos)",
            f"  Depois ({self.change.after_period}): {self.change.after_ratio:.1%} favorável ({self.change.after_cases} casos)",
            f"  Magnitude: {self.change.change_magnitude:.1%}",
            f"  Confiança: {self.change.confidence:.1%}",
            "",
            "ANÁLISE:",
            f"  {self.change.explanation}",
            "",
            "IMPACTO:",
            f"  {self.change.impact_assessment}",
            "",
            "RECOMENDAÇÃO:",
            f"  {self.change.recommended_action}",
        ]

        if self.suggested_strategies:
            lines.append("")
            lines.append("ESTRATÉGIAS SUGERIDAS:")
            for strategy in self.suggested_strategies:
                lines.append(f"  • {strategy}")

        lines.append("")
        lines.append(f"Data: {self.created_at.strftime('%d/%m/%Y %H:%M')}")
        lines.append("=" * 80)

        return "\n".join(lines)


@dataclass
class MonitoringReport:
    """Relatório de monitoramento"""
    generated_at: datetime
    theme: str
    tribunals_monitored: List[str]

    # Período analisado
    period_start: datetime
    period_end: datetime
    total_days: int

    # Mudanças detectadas
    changes_detected: List[ChangeDetection]
    changes_by_tribunal: Dict[str, List[ChangeDetection]]

    # Tendências
    trends: List[TrendAnalysis]

    # Alertas
    alerts: List[MonitoringAlert]

    # Estatísticas
    total_cases_analyzed: int
    tribunals_with_changes: int
    critical_changes: int

    # Highlights
    highlights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def get_critical_alerts(self) -> List[MonitoringAlert]:
        """Retorna apenas alertas críticos e urgentes"""
        return [
            alert for alert in self.alerts
            if alert.priority in ["alta", "urgente"]
        ]

    def get_changes_by_type(self, change_type: str) -> List[ChangeDetection]:
        """Retorna mudanças de um tipo específico"""
        return [
            change for change in self.changes_detected
            if change.change_type == change_type
        ]


@dataclass
class MonitoringConfig:
    """Configuração de monitoramento"""
    themes: List[str]  # Temas a monitorar
    tribunals: List[str]  # Tribunais a monitorar

    # Janelas temporais
    short_term_days: int = 90  # Curto prazo
    medium_term_days: int = 365  # Médio prazo
    long_term_days: int = 730  # Longo prazo (2 anos)

    # Sensibilidade
    change_threshold: float = 0.20  # Mudança mínima para alertar (20%)
    confidence_threshold: float = 0.70  # Confiança mínima
    min_cases_required: int = 5  # Mínimo de casos para análise

    # Alertas
    alert_on_inversion: bool = True
    alert_on_trend: bool = True
    alert_on_volatility: bool = False

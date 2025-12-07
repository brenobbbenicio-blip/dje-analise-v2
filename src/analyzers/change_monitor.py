"""
Monitor de Mudanças de Entendimento Jurisprudencial
Detecta quando tribunais mudam posicionamento sobre temas
"""
import uuid
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

import openai
from chromadb.api.models.Collection import Collection

from ..models.change_monitor_models import (
    JurisprudenceSnapshot,
    TrendPoint,
    ChangeDetection,
    TrendAnalysis,
    MonitoringAlert,
    MonitoringReport,
    MonitoringConfig
)
from ..config import OPENAI_API_KEY, CHAT_MODEL


class ChangeMonitor:
    """
    Monitor de mudanças jurisprudenciais
    Detecta alterações de entendimento ao longo do tempo
    """

    def __init__(self, collection: Collection, config: Optional[MonitoringConfig] = None):
        """
        Inicializa monitor

        Args:
            collection: Coleção ChromaDB
            config: Configuração de monitoramento
        """
        self.collection = collection
        self.config = config or MonitoringConfig(themes=[], tribunals=[])
        openai.api_key = OPENAI_API_KEY

    def monitor_theme(
        self,
        theme: str,
        tribunals: Optional[List[str]] = None,
        days_back: int = 730
    ) -> MonitoringReport:
        """
        Monitora mudanças em um tema específico

        Args:
            theme: Tema a monitorar
            tribunals: Lista de tribunais (None = todos)
            days_back: Dias para análise histórica

        Returns:
            Relatório de monitoramento
        """
        print(f"\n🔍 Monitorando mudanças: '{theme}'")
        print(f"   Período: últimos {days_back} dias")
        print(f"   Tribunais: {tribunals or 'todos'}")

        # 1. Coletar casos históricos
        cases_by_period = self._collect_historical_cases(theme, tribunals, days_back)
        print(f"\n📊 Casos coletados por período: {len(cases_by_period)} períodos")

        # 2. Analisar tendências
        trends = self._analyze_trends(cases_by_period, theme, tribunals or [])
        print(f"📈 Tendências analisadas: {len(trends)}")

        # 3. Detectar mudanças
        changes = self._detect_changes(trends, theme)
        print(f"🔄 Mudanças detectadas: {len(changes)}")

        # 4. Gerar alertas
        alerts = self._generate_alerts(changes)
        print(f"🔔 Alertas gerados: {len(alerts)}")

        # 5. Criar relatório
        report = self._create_report(
            theme=theme,
            tribunals=tribunals or [],
            changes=changes,
            trends=trends,
            alerts=alerts,
            days_back=days_back
        )

        print(f"\n✅ Monitoramento concluído!")
        return report

    def _collect_historical_cases(
        self,
        theme: str,
        tribunals: Optional[List[str]],
        days_back: int
    ) -> Dict[str, List[Dict]]:
        """Coleta casos históricos por período"""
        # Buscar casos relevantes
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=theme
        )
        query_embedding = response.data[0].embedding

        # Buscar no ChromaDB
        where_filter = None
        if tribunals:
            where_filter = {"tribunal": {"$in": tribunals}}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=100,  # Máximo de casos
            where=where_filter,
            include=['documents', 'metadatas', 'distances']
        )

        # Organizar por período
        cases_by_period = defaultdict(list)

        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]

                # Extrair ano
                year = metadata.get('year')
                if not year:
                    continue

                # Criar período (semestral)
                period = f"{year}-S1" if True else f"{year}-S2"  # Simplificado

                case_data = {
                    'id': results['ids'][0][i],
                    'text': doc,
                    'metadata': metadata,
                    'tribunal': metadata.get('tribunal', 'N/A'),
                    'year': year,
                    'decision_type': self._detect_decision(doc)
                }

                cases_by_period[period].append(case_data)

        return dict(cases_by_period)

    def _detect_decision(self, text: str) -> str:
        """Detecta tipo de decisão (favorável/desfavorável)"""
        text_lower = text.lower()

        favorable_patterns = [
            r'\bprovid[oa]\b',
            r'\bdeferid[oa]\b',
            r'\bprocedente\b',
            r'\bacolh\w+\b'
        ]

        unfavorable_patterns = [
            r'\bn[ãa]o[- ]provid[oa]\b',
            r'\bindeferid[oa]\b',
            r'\bimprocedente\b',
            r'\brejeit\w+\b'
        ]

        for pattern in favorable_patterns:
            if re.search(pattern, text_lower):
                return "favorável"

        for pattern in unfavorable_patterns:
            if re.search(pattern, text_lower):
                return "desfavorável"

        return "neutro"

    def _analyze_trends(
        self,
        cases_by_period: Dict[str, List[Dict]],
        theme: str,
        tribunals: List[str]
    ) -> List[TrendAnalysis]:
        """Analisa tendências por tribunal"""
        trends = []

        # Agrupar por tribunal
        cases_by_tribunal = defaultdict(lambda: defaultdict(list))

        for period, cases in cases_by_period.items():
            for case in cases:
                tribunal = case['tribunal']
                cases_by_tribunal[tribunal][period].append(case)

        # Analisar cada tribunal
        for tribunal, tribunal_periods in cases_by_tribunal.items():
            trend = self._calculate_trend(tribunal, theme, tribunal_periods)
            if trend:
                trends.append(trend)

        return trends

    def _calculate_trend(
        self,
        tribunal: str,
        theme: str,
        periods: Dict[str, List[Dict]]
    ) -> Optional[TrendAnalysis]:
        """Calcula tendência para um tribunal"""
        if not periods:
            return None

        trend_points = []
        favorable_ratios = []

        # Calcular ratio para cada período
        for period in sorted(periods.keys()):
            cases = periods[period]
            if len(cases) < 3:  # Mínimo de casos
                continue

            favorable = sum(1 for c in cases if c['decision_type'] == "favorável")
            total = len(cases)
            ratio = favorable / total if total > 0 else 0.0

            favorable_ratios.append(ratio)

            # Criar ponto de tendência
            point = TrendPoint(
                date=datetime.now(),  # Simplificado
                favorable_ratio=ratio,
                total_cases=total,
                representative_case=cases[0] if cases else None
            )
            trend_points.append(point)

        if not trend_points:
            return None

        # Determinar tendência geral
        overall_trend = self._determine_trend_direction(favorable_ratios)
        volatility = self._calculate_volatility(favorable_ratios)

        return TrendAnalysis(
            tribunal=tribunal,
            theme=theme,
            period_start=datetime.now() - timedelta(days=730),
            period_end=datetime.now(),
            trend_points=trend_points,
            overall_trend=overall_trend,
            trend_strength=abs(favorable_ratios[-1] - favorable_ratios[0]) if len(favorable_ratios) > 1 else 0.0,
            volatility=volatility,
            average_favorable_ratio=sum(favorable_ratios) / len(favorable_ratios),
            max_favorable_ratio=max(favorable_ratios),
            min_favorable_ratio=min(favorable_ratios),
            total_cases_analyzed=sum(p.total_cases for p in trend_points)
        )

    def _determine_trend_direction(self, ratios: List[float]) -> str:
        """Determina direção da tendência"""
        if len(ratios) < 2:
            return "estável"

        first_half = sum(ratios[:len(ratios)//2]) / (len(ratios)//2)
        second_half = sum(ratios[len(ratios)//2:]) / (len(ratios) - len(ratios)//2)

        diff = second_half - first_half

        if abs(diff) < 0.1:
            return "estável"
        elif diff > 0.2:
            return "crescente"
        elif diff < -0.2:
            return "decrescente"
        else:
            return "volátil"

    def _calculate_volatility(self, ratios: List[float]) -> float:
        """Calcula volatilidade"""
        if len(ratios) < 2:
            return 0.0

        mean = sum(ratios) / len(ratios)
        variance = sum((r - mean) ** 2 for r in ratios) / len(ratios)
        return variance ** 0.5

    def _detect_changes(
        self,
        trends: List[TrendAnalysis],
        theme: str
    ) -> List[ChangeDetection]:
        """Detecta mudanças significativas"""
        changes = []

        for trend in trends:
            if len(trend.trend_points) < 2:
                continue

            # Comparar primeiro e último período
            first_period = trend.trend_points[0]
            last_period = trend.trend_points[-1]

            change_magnitude = abs(last_period.favorable_ratio - first_period.favorable_ratio)

            # Mudança significativa?
            if change_magnitude >= self.config.change_threshold:
                change = self._analyze_change(trend, first_period, last_period, theme)
                if change:
                    changes.append(change)

        return changes

    def _analyze_change(
        self,
        trend: TrendAnalysis,
        before: TrendPoint,
        after: TrendPoint,
        theme: str
    ) -> Optional[ChangeDetection]:
        """Analisa uma mudança detectada"""
        change_magnitude = abs(after.favorable_ratio - before.favorable_ratio)

        # Determinar tipo de mudança
        if before.favorable_ratio > 0.7 and after.favorable_ratio < 0.3:
            change_type = "inversão_total"
            severity = "crítica"
        elif after.favorable_ratio < before.favorable_ratio - 0.3:
            change_type = "endurecimento"
            severity = "alta"
        elif after.favorable_ratio > before.favorable_ratio + 0.3:
            change_type = "flexibilização"
            severity = "alta"
        elif trend.volatility > 0.3:
            change_type = "divergência"
            severity = "média"
        else:
            change_type = "consolidação"
            severity = "baixa"

        # Gerar explicação com IA
        explanation, impact, recommendation = self._ai_analyze_change(
            trend, before, after, change_type
        )

        return ChangeDetection(
            id=str(uuid.uuid4()),
            tribunal=trend.tribunal,
            theme=theme,
            change_type=change_type,
            severity=severity,
            before_period="Período anterior",
            before_ratio=before.favorable_ratio,
            before_cases=before.total_cases,
            after_period="Período recente",
            after_ratio=after.favorable_ratio,
            after_cases=after.total_cases,
            change_magnitude=change_magnitude,
            confidence=min(1.0, (before.total_cases + after.total_cases) / 20),
            detected_at=datetime.now(),
            explanation=explanation,
            impact_assessment=impact,
            recommended_action=recommendation
        )

    def _ai_analyze_change(
        self,
        trend: TrendAnalysis,
        before: TrendPoint,
        after: TrendPoint,
        change_type: str
    ) -> Tuple[str, str, str]:
        """Usa IA para analisar mudança"""
        prompt = f"""Analise esta mudança jurisprudencial:

Tribunal: {trend.tribunal}
Tema: {trend.theme}
Tipo: {change_type}

Antes: {before.favorable_ratio:.1%} favorável ({before.total_cases} casos)
Depois: {after.favorable_ratio:.1%} favorável ({after.total_cases} casos)
Tendência geral: {trend.overall_trend}

Forneça em JSON:
{{
  "explanation": "Explicação clara da mudança em 2-3 frases",
  "impact": "Impacto prático para advogados e partes",
  "recommendation": "Recomendação estratégica clara"
}}"""

        try:
            response = openai.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "Você é especialista em jurimetria eleitoral."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return (
                result.get('explanation', 'Mudança detectada nos padrões decisórios'),
                result.get('impact', 'Impacto significativo nas estratégias processuais'),
                result.get('recommendation', 'Acompanhar evolução e adaptar estratégia')
            )

        except Exception as e:
            print(f"⚠️  Erro na análise IA: {e}")
            return (
                f"Mudança {change_type} detectada no entendimento do tribunal",
                "Requer atenção às novas decisões",
                "Revisar estratégia processual à luz da nova tendência"
            )

    def _generate_alerts(self, changes: List[ChangeDetection]) -> List[MonitoringAlert]:
        """Gera alertas a partir de mudanças"""
        alerts = []

        for change in changes:
            priority = self._determine_alert_priority(change)

            alert = MonitoringAlert(
                id=str(uuid.uuid4()),
                change=change,
                priority=priority,
                alert_type="mudança_detectada",
                title=f"Mudança em {change.tribunal}: {change.theme}",
                message=f"{change.change_type} detectada",
                actionable=change.severity in ["alta", "crítica"],
                affected_areas=[change.theme],
                suggested_strategies=self._generate_strategies(change)
            )

            alerts.append(alert)

        # Ordenar por prioridade
        priority_order = {"urgente": 0, "alta": 1, "média": 2, "baixa": 3}
        alerts.sort(key=lambda x: priority_order[x.priority])

        return alerts

    def _determine_alert_priority(self, change: ChangeDetection) -> str:
        """Determina prioridade do alerta"""
        if change.severity == "crítica":
            return "urgente"
        elif change.severity == "alta":
            return "alta"
        elif change.severity == "média":
            return "média"
        else:
            return "baixa"

    def _generate_strategies(self, change: ChangeDetection) -> List[str]:
        """Gera estratégias sugeridas"""
        strategies = []

        if change.change_type == "inversão_total":
            strategies.append("Revisar completamente a estratégia processual")
            strategies.append("Buscar precedentes recentes para fundamentação")
        elif change.change_type == "endurecimento":
            strategies.append("Reforçar fundamentação jurídica")
            strategies.append("Considerar teses alternativas")
        elif change.change_type == "flexibilização":
            strategies.append("Aproveitar nova tendência favorável")
            strategies.append("Citar precedentes recentes")

        strategies.append(change.recommended_action)
        return strategies

    def _create_report(
        self,
        theme: str,
        tribunals: List[str],
        changes: List[ChangeDetection],
        trends: List[TrendAnalysis],
        alerts: List[MonitoringAlert],
        days_back: int
    ) -> MonitoringReport:
        """Cria relatório de monitoramento"""
        # Agrupar mudanças por tribunal
        changes_by_tribunal = defaultdict(list)
        for change in changes:
            changes_by_tribunal[change.tribunal].append(change)

        # Contar críticas
        critical = sum(1 for c in changes if c.severity == "crítica")

        # Gerar highlights
        highlights = self._generate_highlights(changes, trends)

        # Gerar recomendações
        recommendations = self._generate_recommendations(changes)

        return MonitoringReport(
            generated_at=datetime.now(),
            theme=theme,
            tribunals_monitored=tribunals or ["Todos"],
            period_start=datetime.now() - timedelta(days=days_back),
            period_end=datetime.now(),
            total_days=days_back,
            changes_detected=changes,
            changes_by_tribunal=dict(changes_by_tribunal),
            trends=trends,
            alerts=alerts,
            total_cases_analyzed=sum(t.total_cases_analyzed for t in trends),
            tribunals_with_changes=len(changes_by_tribunal),
            critical_changes=critical,
            highlights=highlights,
            recommendations=recommendations
        )

    def _generate_highlights(
        self,
        changes: List[ChangeDetection],
        trends: List[TrendAnalysis]
    ) -> List[str]:
        """Gera highlights do monitoramento"""
        highlights = []

        if not changes:
            highlights.append("✅ Nenhuma mudança significativa detectada - jurisprudência estável")
            return highlights

        critical = [c for c in changes if c.severity == "crítica"]
        if critical:
            highlights.append(f"🚨 {len(critical)} mudança(ões) CRÍTICA(S) detectada(s)")

        inversions = [c for c in changes if c.change_type == "inversão_total"]
        if inversions:
            highlights.append(f"🔄 {len(inversions)} inversão(ões) total de entendimento")

        return highlights

    def _generate_recommendations(self, changes: List[ChangeDetection]) -> List[str]:
        """Gera recomendações"""
        recommendations = []

        if not changes:
            recommendations.append("Continue monitorando periodicamente")
            return recommendations

        critical = [c for c in changes if c.severity in ["alta", "crítica"]]
        if critical:
            recommendations.append("🚨 URGENTE: Revisar estratégias processuais em andamento")

        recommendations.append("📊 Acompanhar próximas decisões para confirmar tendência")
        recommendations.append("📚 Atualizar fundamentação com precedentes recentes")

        return recommendations

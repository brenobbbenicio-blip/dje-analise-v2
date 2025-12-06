"""
Gerador de relatórios formatados para análise de contradições
"""
from typing import List
from datetime import datetime

from ..models.contradiction_models import (
    Contradiction,
    ContradictionReport,
    ContradictionCluster,
    ContradictionAlert
)


class ReportGenerator:
    """Gerador de relatórios formatados para terminal e arquivos"""

    @staticmethod
    def format_terminal_report(report: ContradictionReport) -> str:
        """
        Formata relatório completo para exibição no terminal

        Args:
            report: Relatório de contradições

        Returns:
            String formatada para terminal
        """
        lines = []

        # Header
        lines.append("=" * 100)
        lines.append("🔍 RELATÓRIO DE ANÁLISE DE CONTRADIÇÕES JURISPRUDENCIAIS")
        lines.append("=" * 100)
        lines.append(f"\n📅 Gerado em: {report.generated_at.strftime('%d/%m/%Y às %H:%M:%S')}")
        lines.append(f"🔎 Consulta: {report.query}")
        lines.append(f"📊 Casos analisados: {report.total_cases_analyzed}")
        lines.append(f"⚠️  Contradições encontradas: {report.contradictions_found}")

        # Highlights
        if report.highlights:
            lines.append("\n" + "=" * 100)
            lines.append("🌟 PRINCIPAIS DESCOBERTAS")
            lines.append("=" * 100)
            for highlight in report.highlights:
                lines.append(f"  {highlight}")

        # Contradições críticas
        critical = report.get_critical_contradictions()
        if critical:
            lines.append("\n" + "=" * 100)
            lines.append("🚨 CONTRADIÇÕES CRÍTICAS - ATENÇÃO URGENTE")
            lines.append("=" * 100)
            for i, contradiction in enumerate(critical, 1):
                lines.append(ReportGenerator._format_contradiction(contradiction, i))

        # Clusters
        if report.clusters:
            lines.append("\n" + "=" * 100)
            lines.append("📂 CONTRADIÇÕES POR TEMA")
            lines.append("=" * 100)

            for cluster in report.clusters:
                lines.append(ReportGenerator._format_cluster(cluster))

        # Estatísticas por tribunal
        if report.tribunal_comparison:
            lines.append("\n" + "=" * 100)
            lines.append("⚖️  ANÁLISE POR TRIBUNAL")
            lines.append("=" * 100)
            lines.append(ReportGenerator._format_tribunal_stats(report.tribunal_comparison))

        # Recomendações
        if report.recommendations:
            lines.append("\n" + "=" * 100)
            lines.append("💡 RECOMENDAÇÕES ESTRATÉGICAS")
            lines.append("=" * 100)
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"  {i}. {rec}")

        # Footer
        lines.append("\n" + "=" * 100)
        lines.append("✅ Fim do relatório")
        lines.append("=" * 100)

        return "\n".join(lines)

    @staticmethod
    def _format_contradiction(contradiction: Contradiction, index: int = 1) -> str:
        """Formata uma contradição individual"""
        severity_emoji = {
            "baixa": "ℹ️",
            "média": "⚠️",
            "alta": "🔴",
            "crítica": "🚨"
        }

        type_labels = {
            "decisao_oposta": "Decisão Oposta",
            "fundamento_diverso": "Fundamento Diverso",
            "interpretacao_divergente": "Interpretação Divergente",
            "criterio_conflitante": "Critério Conflitante"
        }

        lines = [
            f"\n{severity_emoji[contradiction.contradiction_severity]} CONTRADIÇÃO #{index} - Gravidade: {contradiction.contradiction_severity.upper()}",
            f"{'─' * 80}",
            f"🔹 Tipo: {type_labels.get(contradiction.contradiction_type, contradiction.contradiction_type)}",
            f"🔹 Similaridade: {contradiction.similarity_score:.1%}",
            f"",
            f"📋 CASO 1: {contradiction.case1.tribunal}",
            f"   {contradiction.case1.title}",
            f"   Decisão: {contradiction.case1.decision_type or 'N/A'}",
            f"",
            f"📋 CASO 2: {contradiction.case2.tribunal}",
            f"   {contradiction.case2.title}",
            f"   Decisão: {contradiction.case2.decision_type or 'N/A'}",
            f"",
            f"💭 ANÁLISE:",
            f"   {contradiction.explanation}",
            f"",
            f"⚖️  IMPACTO JURÍDICO:",
            f"   {contradiction.legal_impact}",
            f"",
            f"💡 RECOMENDAÇÃO:",
            f"   {contradiction.recommended_action}",
        ]

        return "\n".join(lines)

    @staticmethod
    def _format_cluster(cluster: ContradictionCluster) -> str:
        """Formata um cluster de contradições"""
        lines = [
            f"\n📂 TEMA: {cluster.theme}",
            f"{'─' * 80}",
            f"   Contradições: {len(cluster.contradictions)}",
            f"   Tribunais afetados: {', '.join(cluster.affected_tribunals)}",
            f"   Casos envolvidos: {cluster.total_cases}",
        ]

        # Distribuição de gravidade
        if cluster.severity_distribution:
            severity_str = ", ".join([
                f"{sev}: {count}" for sev, count in cluster.severity_distribution.items()
            ])
            lines.append(f"   Gravidade: {severity_str}")

        lines.append(f"\n   {cluster.summary}")

        # Listar contradições do cluster
        for i, contradiction in enumerate(cluster.contradictions, 1):
            severity_emoji = {
                "baixa": "ℹ️",
                "média": "⚠️",
                "alta": "🔴",
                "crítica": "🚨"
            }
            emoji = severity_emoji.get(contradiction.contradiction_severity, "•")
            lines.append(
                f"   {emoji} {contradiction.case1.tribunal} vs {contradiction.case2.tribunal} "
                f"(similaridade: {contradiction.similarity_score:.1%})"
            )

        return "\n".join(lines)

    @staticmethod
    def _format_tribunal_stats(stats: dict) -> str:
        """Formata estatísticas por tribunal"""
        lines = []

        # Cabeçalho
        lines.append(f"\n{'Tribunal':<15} {'Casos':<10} {'Contradições':<15} {'Taxa':<10} {'Distribuição'}")
        lines.append("─" * 80)

        # Dados
        for tribunal, data in sorted(stats.items()):
            cases = data['total_cases']
            contradictions = data['contradictions_involved']
            rate = data['contradiction_rate']

            severity_dist = data.get('severity_distribution', {})
            dist_str = ", ".join([
                f"{sev[0].upper()}: {count}"
                for sev, count in severity_dist.items()
            ]) if severity_dist else "-"

            lines.append(
                f"{tribunal:<15} {cases:<10} {contradictions:<15} "
                f"{rate:>8.1%}  {dist_str}"
            )

        return "\n".join(lines)

    @staticmethod
    def format_alert(alert: ContradictionAlert) -> str:
        """Formata um alerta individual"""
        return alert.format_alert()

    @staticmethod
    def format_summary(report: ContradictionReport) -> str:
        """Gera resumo executivo do relatório"""
        lines = [
            "📊 RESUMO EXECUTIVO",
            "=" * 80,
            f"Consulta: {report.query}",
            f"Casos analisados: {report.total_cases_analyzed}",
            f"Contradições encontradas: {report.contradictions_found}",
            f"Clusters temáticos: {len(report.clusters)}",
            ""
        ]

        if report.contradictions_found > 0:
            critical = report.get_critical_contradictions()
            lines.append(f"⚠️  Contradições críticas: {len(critical)}")

            if report.clusters:
                top_theme = report.clusters[0]
                lines.append(f"🔥 Tema mais problemático: {top_theme.theme} ({len(top_theme.contradictions)} contradições)")

        if report.highlights:
            lines.append("\n🌟 Principais achados:")
            for highlight in report.highlights[:3]:
                lines.append(f"   • {highlight}")

        return "\n".join(lines)

    @staticmethod
    def export_to_markdown(report: ContradictionReport, filepath: str) -> None:
        """
        Exporta relatório para arquivo Markdown

        Args:
            report: Relatório a exportar
            filepath: Caminho do arquivo de saída
        """
        lines = []

        # Header
        lines.append("# 🔍 Relatório de Análise de Contradições Jurisprudenciais\n")
        lines.append(f"**Gerado em:** {report.generated_at.strftime('%d/%m/%Y às %H:%M:%S')}  ")
        lines.append(f"**Consulta:** {report.query}  ")
        lines.append(f"**Casos analisados:** {report.total_cases_analyzed}  ")
        lines.append(f"**Contradições encontradas:** {report.contradictions_found}  \n")

        # Highlights
        if report.highlights:
            lines.append("## 🌟 Principais Descobertas\n")
            for highlight in report.highlights:
                lines.append(f"- {highlight}")
            lines.append("")

        # Contradições críticas
        critical = report.get_critical_contradictions()
        if critical:
            lines.append("## 🚨 Contradições Críticas\n")
            for i, contradiction in enumerate(critical, 1):
                lines.append(f"### Contradição #{i}\n")
                lines.append(f"**Tipo:** {contradiction.contradiction_type}  ")
                lines.append(f"**Gravidade:** {contradiction.contradiction_severity}  ")
                lines.append(f"**Similaridade:** {contradiction.similarity_score:.1%}  \n")
                lines.append(f"**Caso 1:** {contradiction.case1.tribunal} - {contradiction.case1.title}  ")
                lines.append(f"**Caso 2:** {contradiction.case2.tribunal} - {contradiction.case2.title}  \n")
                lines.append(f"**Análise:** {contradiction.explanation}\n")
                lines.append(f"**Impacto:** {contradiction.legal_impact}\n")
                lines.append(f"**Recomendação:** {contradiction.recommended_action}\n")

        # Clusters
        if report.clusters:
            lines.append("## 📂 Contradições por Tema\n")
            for cluster in report.clusters:
                lines.append(f"### {cluster.theme}\n")
                lines.append(f"- **Contradições:** {len(cluster.contradictions)}")
                lines.append(f"- **Tribunais:** {', '.join(cluster.affected_tribunals)}")
                lines.append(f"- **Casos:** {cluster.total_cases}\n")
                lines.append(f"{cluster.summary}\n")

        # Recomendações
        if report.recommendations:
            lines.append("## 💡 Recomendações Estratégicas\n")
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        # Salvar arquivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        print(f"✅ Relatório exportado para: {filepath}")

    @staticmethod
    def export_to_json(report: ContradictionReport, filepath: str) -> None:
        """
        Exporta relatório para arquivo JSON

        Args:
            report: Relatório a exportar
            filepath: Caminho do arquivo de saída
        """
        import json

        # Converter para dict
        data = {
            'metadata': {
                'generated_at': report.generated_at.isoformat(),
                'query': report.query,
                'total_cases_analyzed': report.total_cases_analyzed,
                'contradictions_found': report.contradictions_found
            },
            'highlights': report.highlights,
            'recommendations': report.recommendations,
            'clusters': [
                {
                    'theme': cluster.theme,
                    'contradictions_count': len(cluster.contradictions),
                    'affected_tribunals': cluster.affected_tribunals,
                    'total_cases': cluster.total_cases,
                    'severity_distribution': cluster.severity_distribution,
                    'summary': cluster.summary
                }
                for cluster in report.clusters
            ],
            'tribunal_comparison': report.tribunal_comparison,
            'contradictions': [
                {
                    'id': c.id,
                    'type': c.contradiction_type,
                    'severity': c.contradiction_severity,
                    'similarity': c.similarity_score,
                    'case1': {
                        'tribunal': c.case1.tribunal,
                        'title': c.case1.title,
                        'decision_type': c.case1.decision_type
                    },
                    'case2': {
                        'tribunal': c.case2.tribunal,
                        'title': c.case2.title,
                        'decision_type': c.case2.decision_type
                    },
                    'explanation': c.explanation,
                    'legal_impact': c.legal_impact,
                    'recommended_action': c.recommended_action
                }
                for cluster in report.clusters
                for c in cluster.contradictions
            ]
        }

        # Salvar
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ Relatório JSON exportado para: {filepath}")

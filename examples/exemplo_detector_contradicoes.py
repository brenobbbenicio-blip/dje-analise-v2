"""
Exemplo de uso do Detector de Contradições Jurisprudenciais

Este script demonstra como usar programaticamente o detector de contradições
em vez de usar a interface CLI.
"""
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import RAGSystem
from src.analyzers import ContradictionDetector, ReportGenerator


def exemplo_basico():
    """Exemplo básico de detecção de contradições"""
    print("=" * 80)
    print("EXEMPLO 1: Uso Básico do Detector de Contradições")
    print("=" * 80)

    # 1. Inicializar sistema RAG
    print("\n1. Inicializando sistema RAG...")
    rag = RAGSystem()

    # Verificar se há documentos
    stats = rag.get_stats()
    if stats['total_documents'] == 0:
        print("⚠️  Base de dados vazia! Execute primeiro:")
        print("   python main.py --setup")
        return

    print(f"   ✓ {stats['total_documents']} documentos carregados")

    # 2. Criar detector
    print("\n2. Criando detector de contradições...")
    detector = ContradictionDetector(rag.collection)
    print("   ✓ Detector inicializado")

    # 3. Detectar contradições
    print("\n3. Detectando contradições para tema 'registro de candidatura'...")
    report = detector.detect_contradictions(
        query="registro de candidatura",
        similarity_threshold=0.75,
        max_cases=30
    )

    # 4. Exibir resultados
    print("\n4. Resultados:")
    print(f"   Casos analisados: {report.total_cases_analyzed}")
    print(f"   Contradições encontradas: {report.contradictions_found}")

    if report.contradictions_found > 0:
        print("\n5. Principais descobertas:")
        for highlight in report.highlights:
            print(f"   • {highlight}")

        # Mostrar contradições críticas
        critical = report.get_critical_contradictions()
        if critical:
            print(f"\n⚠️  {len(critical)} contradição(ões) CRÍTICA(S) detectada(s)!")
            for i, c in enumerate(critical, 1):
                print(f"\n   Contradição Crítica #{i}:")
                print(f"   {c.case1.tribunal} vs {c.case2.tribunal}")
                print(f"   Similaridade: {c.similarity_score:.1%}")
                print(f"   Explicação: {c.explanation[:100]}...")


def exemplo_filtrado_por_tribunal():
    """Exemplo com filtro de tribunais"""
    print("\n\n" + "=" * 80)
    print("EXEMPLO 2: Análise Filtrada por Tribunais")
    print("=" * 80)

    # Inicializar
    rag = RAGSystem()
    detector = ContradictionDetector(rag.collection)

    # Analisar apenas tribunais da região Norte
    print("\nAnalisando contradições na Região Norte...")
    tribunais_norte = ["TRE-PA", "TRE-RO", "TRE-AM", "TRE-AP"]

    report = detector.detect_contradictions(
        query="propaganda eleitoral",
        similarity_threshold=0.75,
        max_cases=20,
        tribunal_filter=tribunais_norte
    )

    print(f"\nResultados para {', '.join(tribunais_norte)}:")
    print(f"  Casos analisados: {report.total_cases_analyzed}")
    print(f"  Contradições: {report.contradictions_found}")

    if report.clusters:
        print("\nClusters temáticos:")
        for cluster in report.clusters:
            print(f"  • {cluster.theme}: {len(cluster.contradictions)} contradição(ões)")


def exemplo_exportacao():
    """Exemplo de exportação de relatórios"""
    print("\n\n" + "=" * 80)
    print("EXEMPLO 3: Exportação de Relatórios")
    print("=" * 80)

    # Inicializar
    rag = RAGSystem()
    detector = ContradictionDetector(rag.collection)

    # Detectar contradições
    print("\nDetectando contradições sobre 'inelegibilidade'...")
    report = detector.detect_contradictions(
        query="inelegibilidade",
        similarity_threshold=0.75,
        max_cases=25
    )

    # Exportar para Markdown
    print("\nExportando para Markdown...")
    md_path = "exemplo_relatorio.md"
    ReportGenerator.export_to_markdown(report, md_path)
    print(f"✓ Exportado para: {md_path}")

    # Exportar para JSON
    print("\nExportando para JSON...")
    json_path = "exemplo_relatorio.json"
    ReportGenerator.export_to_json(report, json_path)
    print(f"✓ Exportado para: {json_path}")


def exemplo_alertas():
    """Exemplo de criação de alertas"""
    print("\n\n" + "=" * 80)
    print("EXEMPLO 4: Geração de Alertas")
    print("=" * 80)

    # Inicializar
    rag = RAGSystem()
    detector = ContradictionDetector(rag.collection)

    # Detectar contradições
    print("\nDetectando contradições sobre 'abuso de poder'...")
    report = detector.detect_contradictions(
        query="abuso de poder",
        similarity_threshold=0.8,
        max_cases=30
    )

    # Criar alertas
    if report.contradictions_found > 0:
        print("\nCriando alertas...")

        all_contradictions = []
        for cluster in report.clusters:
            all_contradictions.extend(cluster.contradictions)

        alerts = detector.create_alerts(
            all_contradictions,
            priority_threshold="média"
        )

        print(f"\n{len(alerts)} alerta(s) criado(s)")

        # Mostrar alertas de alta prioridade
        high_priority = [a for a in alerts if a.priority in ["alta", "urgente"]]
        if high_priority:
            print(f"\n⚠️  {len(high_priority)} alerta(s) de ALTA PRIORIDADE:\n")
            for alert in high_priority[:2]:  # Mostrar 2 primeiros
                print(ReportGenerator.format_alert(alert))
                print()


def exemplo_analise_customizada():
    """Exemplo de análise customizada"""
    print("\n\n" + "=" * 80)
    print("EXEMPLO 5: Análise Customizada")
    print("=" * 80)

    # Inicializar
    rag = RAGSystem()
    detector = ContradictionDetector(rag.collection)

    # Detectar contradições com configuração agressiva
    print("\nAnálise com alta precisão (similarity 0.85)...")
    report = detector.detect_contradictions(
        query="fake news eleições",
        similarity_threshold=0.85,  # Mais restritivo
        max_cases=50
    )

    print(f"\nResultados:")
    print(f"  Casos analisados: {report.total_cases_analyzed}")
    print(f"  Contradições: {report.contradictions_found}")

    # Análise por tribunal
    print("\nAnálise por tribunal:")
    for tribunal, stats in report.tribunal_comparison.items():
        if stats['total_cases'] > 0:
            print(f"  {tribunal}:")
            print(f"    Casos: {stats['total_cases']}")
            print(f"    Contradições: {stats['contradictions_involved']}")
            print(f"    Taxa: {stats['contradiction_rate']:.1%}")

    # Recomendações
    if report.recommendations:
        print("\nRecomendações estratégicas:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")


def exemplo_relatorio_completo():
    """Exemplo de relatório completo formatado"""
    print("\n\n" + "=" * 80)
    print("EXEMPLO 6: Relatório Completo Formatado")
    print("=" * 80)

    # Inicializar
    rag = RAGSystem()
    detector = ContradictionDetector(rag.collection)

    # Detectar contradições
    print("\nGerando relatório completo...")
    report = detector.detect_contradictions(
        query="direitos políticos",
        similarity_threshold=0.75,
        max_cases=40
    )

    # Formatar e exibir relatório completo
    print("\n" + "=" * 100)
    formatted_report = ReportGenerator.format_terminal_report(report)
    print(formatted_report)


def main():
    """Executa todos os exemplos"""
    print("\n🔍 EXEMPLOS DE USO DO DETECTOR DE CONTRADIÇÕES")
    print("=" * 80)

    try:
        # Executar exemplos
        exemplo_basico()
        exemplo_filtrado_por_tribunal()
        exemplo_exportacao()
        exemplo_alertas()
        exemplo_analise_customizada()

        # Perguntar se quer ver relatório completo
        print("\n" + "=" * 80)
        print("\nDeseja ver um exemplo de relatório completo? (s/n): ", end="")
        if input().lower() == 's':
            exemplo_relatorio_completo()

    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ Exemplos concluídos!")
    print("=" * 80)


if __name__ == "__main__":
    main()

"""
Interface principal do sistema de análise de jurisprudência
"""
import sys
import argparse
from pathlib import Path

from src.models import RAGSystem
from src.scraper import DJEScraper
from src.embeddings import DocumentProcessor
from src.analyzers import ContradictionDetector, ReportGenerator
from src.generators import DocumentGenerator, DocumentTemplates
from src.models.document_models import GenerationRequest, Party
from src.utils import (
    format_result,
    save_result,
    print_banner,
    validate_api_key
)
from src.config import (
    OPENAI_API_KEY,
    PROCESSED_DATA_DIR,
    AVAILABLE_TRIBUNALS,
    TRE_CONFIGS
)


def setup_database(max_docs: int = 2, tribunals: list = None, use_scraping: bool = False):
    """
    Configura a base de dados com documentos de exemplo ou raspagem real

    Args:
        max_docs: Número máximo de documentos por tribunal
        tribunals: Lista de tribunais a coletar (None = todos)
        use_scraping: Se True, tenta fazer raspagem real dos sites
    """
    print("\n🔧 Configurando base de dados...")

    if use_scraping:
        print("🌐 Modo: RASPAGEM REAL (com fallback para exemplos)")
    else:
        print("📄 Modo: DOCUMENTOS DE EXEMPLO")

    if tribunals is None:
        tribunals = AVAILABLE_TRIBUNALS
        print(f"📋 Coletando de todos os tribunais: {', '.join(tribunals)}")
    else:
        print(f"📋 Tribunais selecionados: {', '.join(tribunals)}")

    # Inicializar componentes
    processor = DocumentProcessor()
    rag = RAGSystem()

    all_documents = []

    # Coletar de cada tribunal
    print(f"\n📥 Coletando {max_docs} documentos de cada tribunal...")
    print("=" * 80)

    for tribunal in tribunals:
        scraper = DJEScraper(tribunal=tribunal, use_real_scraping=use_scraping)

        docs = scraper.scrape_search_results(
            search_term="eleições",
            max_results=max_docs
        )

        # Salvar documentos brutos por tribunal
        filename = f"jurisprudencia_{tribunal.lower()}.json"
        scraper.save_documents(docs, filename)

        all_documents.extend(docs)
        print()  # Linha em branco entre tribunais

    print("=" * 80)
    print(f"\n⚙️  Processando {len(all_documents)} documentos...")
    processed_docs = processor.process_documents(all_documents)

    print(f"💾 Adicionando documentos ao vectorstore...")
    rag.add_documents(processed_docs)

    stats = rag.get_stats(by_tribunal=True)
    print(f"\n✅ Base de dados configurada!")
    print(f"   Total de documentos: {stats['total_documents']}")

    if 'by_tribunal' in stats:
        print("\n   Documentos por tribunal:")
        for trib, count in stats['by_tribunal'].items():
            if count > 0:
                print(f"   - {trib}: {count} documentos")


def query_system(question: str, tribunal_filter: str = None, save: bool = False):
    """
    Realiza consulta no sistema

    Args:
        question: Pergunta do usuário
        tribunal_filter: Filtrar por tribunal específico
        save: Se deve salvar o resultado
    """
    if tribunal_filter:
        print(f"\n🔍 Processando consulta em {tribunal_filter}...")
    else:
        print("\n🔍 Processando consulta em todos os tribunais...")

    # Inicializar RAG
    rag = RAGSystem()

    # Verificar se há documentos
    stats = rag.get_stats()
    if stats['total_documents'] == 0:
        print("\n⚠️  Base de dados vazia!")
        print("Execute primeiro: python main.py --setup")
        return

    # Fazer consulta
    result = rag.query(question, tribunal_filter=tribunal_filter)

    # Formatar e exibir resultado
    formatted = format_result(result)
    print(formatted)

    # Salvar se solicitado
    if save:
        filepath = save_result(result, PROCESSED_DATA_DIR)
        print(f"💾 Resultado salvo em: {filepath}")


def detect_contradictions_cmd(
    query: str,
    similarity_threshold: float = 0.75,
    max_cases: int = 50,
    tribunals: list = None,
    export_format: str = None
):
    """
    Detecta contradições jurisprudenciais

    Args:
        query: Consulta/tema para análise
        similarity_threshold: Limiar de similaridade (0.0 a 1.0)
        max_cases: Número máximo de casos a analisar
        tribunals: Lista de tribunais para filtrar
        export_format: Formato de exportação ('md', 'json' ou None)
    """
    print_banner()
    print("\n🔍 DETECTOR DE CONTRADIÇÕES JURISPRUDENCIAIS")
    print("=" * 100)

    # Inicializar RAG
    rag = RAGSystem()

    # Verificar se há documentos
    stats = rag.get_stats()
    if stats['total_documents'] == 0:
        print("\n⚠️  Base de dados vazia!")
        print("Execute primeiro: python main.py --setup")
        return

    print(f"\n📊 Base de dados: {stats['total_documents']} documentos")

    # Inicializar detector
    detector = ContradictionDetector(rag.collection)

    # Detectar contradições
    report = detector.detect_contradictions(
        query=query,
        similarity_threshold=similarity_threshold,
        max_cases=max_cases,
        tribunal_filter=tribunals
    )

    # Gerar e exibir relatório
    print("\n")
    formatted_report = ReportGenerator.format_terminal_report(report)
    print(formatted_report)

    # Exportar se solicitado
    if export_format:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if export_format == 'md':
            filepath = PROCESSED_DATA_DIR / f"contradictions_{timestamp}.md"
            ReportGenerator.export_to_markdown(report, str(filepath))
        elif export_format == 'json':
            filepath = PROCESSED_DATA_DIR / f"contradictions_{timestamp}.json"
            ReportGenerator.export_to_json(report, str(filepath))

    # Gerar alertas para contradições críticas
    critical = report.get_critical_contradictions()
    if critical:
        print("\n" + "=" * 100)
        print("🚨 ALERTAS CRÍTICOS")
        print("=" * 100)

        alerts = detector.create_alerts(critical, priority_threshold="alta")
        for alert in alerts[:3]:  # Mostrar no máximo 3 alertas
            print(ReportGenerator.format_alert(alert))


def generate_document_cmd(
    document_type: str,
    case_description: str,
    objective: str,
    tribunal: str = "TSE",
    arguments: list = None,
    export_path: str = None
):
    """
    Gera documento processual automaticamente

    Args:
        document_type: Tipo de documento (petição_inicial, recurso, parecer, etc)
        case_description: Descrição do caso
        objective: Objetivo da peça
        tribunal: Tribunal destinatário
        arguments: Lista de argumentos principais
        export_path: Caminho para exportar (opcional)
    """
    print_banner()
    print("\n🤖 GERADOR AUTOMÁTICO DE PEÇAS PROCESSUAIS")
    print("=" * 100)

    # Verificar base de dados
    rag = RAGSystem()
    stats = rag.get_stats()
    if stats['total_documents'] == 0:
        print("\n⚠️  Base de dados vazia! A peça será gerada com jurisprudência limitada.")
        print("Para melhor qualidade, execute: python main.py --setup")
        print()

    # Listar templates disponíveis
    templates = DocumentTemplates.get_all_templates()
    if document_type not in templates:
        print(f"\n❌ Tipo de documento '{document_type}' não disponível.")
        print(f"\nDisponíveis: {', '.join(templates.keys())}")
        return

    template = templates[document_type]
    print(f"\n📋 Tipo: {template.name}")
    print(f"📄 Descrição: {template.description}")
    print(f"⚖️  Tribunal: {tribunal}")

    # Criar requisição
    request = GenerationRequest(
        document_type=document_type,
        tribunal=tribunal,
        case_description=case_description,
        objective=objective,
        main_arguments=arguments or [],
        max_jurisprudence=5
    )

    # Gerar documento
    generator = DocumentGenerator(rag)
    result = generator.generate_document(request)

    # Exibir resultado
    print("\n" + "=" * 100)
    print("📄 DOCUMENTO GERADO")
    print("=" * 100)
    print()
    print(result.formatted_text)
    print()
    print("=" * 100)

    # Estatísticas
    print(f"\n📊 Estatísticas:")
    print(f"   Palavras: {result.word_count}")
    print(f"   Jurisprudências citadas: {result.jurisprudence_count}")
    print(f"   Argumentos desenvolvidos: {result.argument_count}")
    print(f"   Qualidade estimada: {result.quality_score:.1%}")

    # Sugestões
    if result.suggestions:
        print(f"\n💡 Sugestões de melhoria:")
        for sug in result.suggestions:
            print(f"   • {sug}")

    # Exportar se solicitado
    if export_path:
        from pathlib import Path
        export_file = Path(export_path)
        export_file.parent.mkdir(parents=True, exist_ok=True)

        with open(export_file, 'w', encoding='utf-8') as f:
            f.write(result.formatted_text)

        print(f"\n✅ Documento exportado para: {export_path}")
    else:
        # Salvar em processed
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{document_type}_{timestamp}.txt"
        filepath = PROCESSED_DATA_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result.formatted_text)

        print(f"\n💾 Documento salvo em: {filepath}")


def interactive_mode():
    """Modo interativo de consulta"""
    print_banner()

    # Validar API key
    if not validate_api_key(OPENAI_API_KEY):
        print("\n❌ ERRO: API key da OpenAI não configurada!")
        print("Configure a variável OPENAI_API_KEY no arquivo .env")
        return

    # Inicializar RAG
    rag = RAGSystem()

    # Verificar base de dados
    stats = rag.get_stats(by_tribunal=True)
    print(f"\n📊 Base de dados: {stats['total_documents']} documentos")

    if 'by_tribunal' in stats and any(stats['by_tribunal'].values()):
        print("\n   Distribuição por tribunal:")
        for trib, count in stats['by_tribunal'].items():
            if count > 0:
                print(f"   - {trib}: {count} documentos")

    if stats['total_documents'] == 0:
        print("\n⚠️  Base de dados vazia!")
        print("Deseja configurar agora? (s/n): ", end="")
        if input().lower() == 's':
            setup_database()
        else:
            print("Execute: python main.py --setup")
            return

    print("\n" + "=" * 80)
    print("💡 Modo interativo - Digite 'sair' para encerrar")
    print("💡 Para filtrar por tribunal, use: [TRIBUNAL] pergunta")
    print("   Exemplo: [TRE-MG] Quais os requisitos?")
    print("=" * 80)

    while True:
        print("\n📝 Digite sua pergunta sobre jurisprudência eleitoral:")
        print("> ", end="")

        question = input().strip()

        if question.lower() in ['sair', 'exit', 'quit']:
            print("\n👋 Encerrando sistema. Até logo!")
            break

        if not question:
            continue

        try:
            # Verificar se há filtro de tribunal
            tribunal_filter = None
            if question.startswith('[') and ']' in question:
                end_bracket = question.index(']')
                tribunal_filter = question[1:end_bracket].upper()
                question = question[end_bracket+1:].strip()

                if tribunal_filter not in AVAILABLE_TRIBUNALS:
                    print(f"\n⚠️ Tribunal '{tribunal_filter}' não disponível.")
                    print(f"Tribunais disponíveis: {', '.join(AVAILABLE_TRIBUNALS)}")
                    continue

            query_system(question, tribunal_filter=tribunal_filter, save=True)
        except Exception as e:
            print(f"\n❌ Erro ao processar consulta: {e}")
            print("Tente novamente ou digite 'sair' para encerrar.")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Sistema de Análise de Jurisprudência Eleitoral com RAG"
    )

    parser.add_argument(
        '--setup',
        action='store_true',
        help='Configura a base de dados inicial'
    )

    parser.add_argument(
        '--query',
        type=str,
        help='Realiza uma consulta direta'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Inicia modo interativo (padrão)'
    )

    parser.add_argument(
        '--max-docs',
        type=int,
        default=2,
        help='Número máximo de documentos por tribunal ao fazer setup (padrão: 2)'
    )

    parser.add_argument(
        '--tribunal',
        type=str,
        help='Filtrar por tribunal específico (TSE, TRE-MG, TRE-RJ, TRE-PR, TRE-SC)'
    )

    parser.add_argument(
        '--tribunals',
        type=str,
        help='Lista de tribunais para setup, separados por vírgula (ex: TSE,TRE-MG)'
    )

    parser.add_argument(
        '--scrape',
        action='store_true',
        help='Usar raspagem real dos sites (experimental, com fallback para exemplos)'
    )

    parser.add_argument(
        '--detect-contradictions',
        type=str,
        metavar='QUERY',
        help='Detecta contradições jurisprudenciais para um tema/consulta específica'
    )

    parser.add_argument(
        '--similarity',
        type=float,
        default=0.75,
        help='Limiar de similaridade para detecção (0.0 a 1.0, padrão: 0.75)'
    )

    parser.add_argument(
        '--max-cases',
        type=int,
        default=50,
        help='Número máximo de casos a analisar (padrão: 50)'
    )

    parser.add_argument(
        '--export',
        type=str,
        choices=['md', 'json'],
        help='Exportar relatório de contradições (md=Markdown, json=JSON)'
    )

    parser.add_argument(
        '--generate-document',
        type=str,
        metavar='TIPO',
        choices=['petição_inicial', 'recurso', 'parecer', 'impugnação', 'contestação'],
        help='Gera documento processual automaticamente (petição_inicial, recurso, parecer, impugnação, contestação)'
    )

    parser.add_argument(
        '--case-description',
        type=str,
        help='Descrição do caso para geração de documento'
    )

    parser.add_argument(
        '--objective',
        type=str,
        help='Objetivo da peça processual'
    )

    parser.add_argument(
        '--doc-tribunal',
        type=str,
        default='TSE',
        help='Tribunal destinatário do documento (padrão: TSE)'
    )

    parser.add_argument(
        '--arguments',
        type=str,
        help='Argumentos principais separados por ponto-e-vírgula (ex: "inelegibilidade;condições de elegibilidade")'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Caminho para salvar documento gerado'
    )

    args = parser.parse_args()

    # Validar API key
    if not validate_api_key(OPENAI_API_KEY):
        print("\n❌ ERRO: API key da OpenAI não configurada!")
        print("\n📋 Instruções:")
        print("1. Copie o arquivo .env.example para .env")
        print("2. Adicione sua API key da OpenAI no arquivo .env")
        print("3. Execute novamente o programa")
        return 1

    # Executar ação solicitada
    if args.setup:
        tribunals = None
        if args.tribunals:
            tribunals = [t.strip().upper() for t in args.tribunals.split(',')]
            # Validar tribunais
            invalid = [t for t in tribunals if t not in AVAILABLE_TRIBUNALS]
            if invalid:
                print(f"\n❌ Tribunais inválidos: {', '.join(invalid)}")
                print(f"Tribunais disponíveis: {', '.join(AVAILABLE_TRIBUNALS)}")
                return 1

        setup_database(max_docs=args.max_docs, tribunals=tribunals, use_scraping=args.scrape)
    elif args.detect_contradictions:
        tribunals = None
        if args.tribunals:
            tribunals = [t.strip().upper() for t in args.tribunals.split(',')]
            # Validar tribunais
            invalid = [t for t in tribunals if t not in AVAILABLE_TRIBUNALS]
            if invalid:
                print(f"\n❌ Tribunais inválidos: {', '.join(invalid)}")
                print(f"Tribunais disponíveis: {', '.join(AVAILABLE_TRIBUNALS)}")
                return 1

        detect_contradictions_cmd(
            query=args.detect_contradictions,
            similarity_threshold=args.similarity,
            max_cases=args.max_cases,
            tribunals=tribunals,
            export_format=args.export
        )
    elif args.generate_document:
        # Validar parâmetros obrigatórios
        if not args.case_description or not args.objective:
            print("\n❌ ERRO: --case-description e --objective são obrigatórios para geração de documentos!")
            print("\nExemplo:")
            print('python main.py --generate-document recurso \\')
            print('  --case-description "Candidato teve registro indeferido por suposta inelegibilidade" \\')
            print('  --objective "Reformar decisão e deferir registro de candidatura"')
            return 1

        # Processar argumentos
        arguments_list = []
        if args.arguments:
            arguments_list = [arg.strip() for arg in args.arguments.split(';')]

        generate_document_cmd(
            document_type=args.generate_document,
            case_description=args.case_description,
            objective=args.objective,
            tribunal=args.doc_tribunal,
            arguments=arguments_list,
            export_path=args.output
        )
    elif args.query:
        tribunal_filter = None
        if args.tribunal:
            tribunal_filter = args.tribunal.upper()
            if tribunal_filter not in AVAILABLE_TRIBUNALS:
                print(f"\n❌ Tribunal '{tribunal_filter}' não disponível.")
                print(f"Tribunais disponíveis: {', '.join(AVAILABLE_TRIBUNALS)}")
                return 1

        query_system(args.query, tribunal_filter=tribunal_filter, save=True)
    else:
        # Modo interativo (padrão)
        interactive_mode()

    return 0


if __name__ == "__main__":
    sys.exit(main())

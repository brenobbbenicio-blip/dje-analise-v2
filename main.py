"""
Interface principal do sistema de análise de jurisprudência
"""
import sys
import argparse
from pathlib import Path

from src.models import RAGSystem
from src.scraper import DJEScraper
from src.embeddings import DocumentProcessor
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


def setup_database(max_docs: int = 2, tribunals: list = None):
    """
    Configura a base de dados com documentos de exemplo

    Args:
        max_docs: Número máximo de documentos por tribunal
        tribunals: Lista de tribunais a coletar (None = todos)
    """
    print("\n🔧 Configurando base de dados...")

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
        scraper = DJEScraper(tribunal=tribunal)

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

        setup_database(max_docs=args.max_docs, tribunals=tribunals)
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

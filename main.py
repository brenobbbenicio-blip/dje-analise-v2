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
from src.config import OPENAI_API_KEY, PROCESSED_DATA_DIR


def setup_database(max_docs: int = 10):
    """
    Configura a base de dados com documentos de exemplo

    Args:
        max_docs: Número máximo de documentos a coletar
    """
    print("\n🔧 Configurando base de dados...")

    # Inicializar componentes
    scraper = DJEScraper()
    processor = DocumentProcessor()
    rag = RAGSystem()

    # Coletar documentos
    print("\n📥 Coletando documentos de jurisprudência...")
    documents = scraper.scrape_search_results(
        search_term="eleições",
        max_results=max_docs
    )

    # Salvar documentos brutos
    scraper.save_documents(documents, "jurisprudencia_raw.json")

    # Processar documentos
    print("\n⚙️  Processando documentos...")
    processed_docs = processor.process_documents(documents)

    # Adicionar ao vectorstore
    print("\n💾 Adicionando documentos ao vectorstore...")
    rag.add_documents(processed_docs)

    stats = rag.get_stats()
    print(f"\n✅ Base de dados configurada!")
    print(f"   Total de documentos: {stats['total_documents']}")


def query_system(question: str, save: bool = False):
    """
    Realiza consulta no sistema

    Args:
        question: Pergunta do usuário
        save: Se deve salvar o resultado
    """
    print("\n🔍 Processando consulta...")

    # Inicializar RAG
    rag = RAGSystem()

    # Verificar se há documentos
    stats = rag.get_stats()
    if stats['total_documents'] == 0:
        print("\n⚠️  Base de dados vazia!")
        print("Execute primeiro: python main.py --setup")
        return

    # Fazer consulta
    result = rag.query(question)

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
    stats = rag.get_stats()
    print(f"\n📊 Base de dados: {stats['total_documents']} documentos")

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
            query_system(question, save=True)
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
        default=10,
        help='Número máximo de documentos ao fazer setup (padrão: 10)'
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
        setup_database(max_docs=args.max_docs)
    elif args.query:
        query_system(args.query, save=True)
    else:
        # Modo interativo (padrão)
        interactive_mode()

    return 0


if __name__ == "__main__":
    sys.exit(main())

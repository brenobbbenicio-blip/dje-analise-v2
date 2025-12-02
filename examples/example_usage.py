"""
Exemplos de uso do sistema DJE Análise v2
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import RAGSystem
from src.scraper import DJEScraper
from src.embeddings import DocumentProcessor


def example_1_basic_setup():
    """Exemplo 1: Configuração básica do sistema"""
    print("=" * 80)
    print("EXEMPLO 1: Configuração Básica do Sistema")
    print("=" * 80)

    # Inicializar componentes
    scraper = DJEScraper()
    processor = DocumentProcessor()
    rag = RAGSystem()

    # Coletar documentos
    print("\n1. Coletando documentos...")
    documents = scraper.scrape_search_results("registro candidatura", max_results=3)
    print(f"   Coletados: {len(documents)} documentos")

    # Processar documentos
    print("\n2. Processando documentos...")
    processed = processor.process_documents(documents)
    print(f"   Processados: {len(processed)} chunks")

    # Adicionar ao vectorstore
    print("\n3. Adicionando ao vectorstore...")
    rag.add_documents(processed)

    # Verificar estatísticas
    stats = rag.get_stats()
    print(f"\n✅ Sistema configurado com {stats['total_documents']} documentos")


def example_2_simple_query():
    """Exemplo 2: Consulta simples"""
    print("\n" + "=" * 80)
    print("EXEMPLO 2: Consulta Simples")
    print("=" * 80)

    # Inicializar RAG
    rag = RAGSystem()

    # Fazer consulta
    question = "Quais são os requisitos para registro de candidatura?"
    print(f"\nPergunta: {question}")

    result = rag.query(question, n_results=3)

    print("\nResposta:")
    print(result['answer'])

    print("\nFontes consultadas:")
    for i, source in enumerate(result['sources'], 1):
        metadata = source.get('metadata', {})
        print(f"{i}. {metadata.get('title', 'Sem título')}")


def example_3_advanced_query():
    """Exemplo 3: Consulta avançada com análise"""
    print("\n" + "=" * 80)
    print("EXEMPLO 3: Consulta Avançada")
    print("=" * 80)

    rag = RAGSystem()

    # Múltiplas perguntas relacionadas
    questions = [
        "O que caracteriza abuso de poder econômico?",
        "Quais as penalidades para abuso de poder?",
        "Como comprovar abuso de poder econômico?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n--- Pergunta {i} ---")
        print(f"Q: {question}")

        result = rag.query(question, n_results=2)

        print(f"R: {result['answer'][:200]}...")  # Primeiros 200 caracteres
        print(f"Fontes: {len(result['sources'])} documentos consultados")


def example_4_document_processing():
    """Exemplo 4: Processamento de documentos"""
    print("\n" + "=" * 80)
    print("EXEMPLO 4: Processamento de Documentos")
    print("=" * 80)

    processor = DocumentProcessor()

    # Documento de exemplo
    doc = {
        'title': 'Acórdão Teste',
        'text': """Este é um exemplo de acórdão eleitoral.
        A decisão trata sobre registro de candidatura e seus requisitos.
        É importante observar que todos os requisitos legais devem ser cumpridos.
        A Lei das Eleições estabelece critérios claros para a candidatura.
        O descumprimento pode acarretar indeferimento do registro.""",
        'metadata': {
            'number': 'TESTE-001',
            'year': 2024
        }
    }

    print("\nDocumento original:")
    print(f"Título: {doc['title']}")
    print(f"Tamanho: {len(doc['text'])} caracteres")

    # Processar
    processed = processor.process_documents([doc])

    print(f"\nDocumento processado:")
    print(f"Chunks gerados: {len(processed)}")

    for i, chunk in enumerate(processed, 1):
        print(f"\nChunk {i}:")
        print(f"  Tamanho: {len(chunk['text'])} caracteres")
        print(f"  Metadata: {chunk['metadata']}")
        print(f"  Texto: {chunk['text'][:100]}...")


def example_5_scraper_usage():
    """Exemplo 5: Uso do scraper"""
    print("\n" + "=" * 80)
    print("EXEMPLO 5: Uso do Scraper")
    print("=" * 80)

    scraper = DJEScraper()

    # Coletar documentos
    print("\n1. Coletando documentos sobre 'propaganda eleitoral'...")
    docs = scraper.scrape_search_results("propaganda eleitoral", max_results=2)

    print(f"\nDocumentos coletados: {len(docs)}")

    for i, doc in enumerate(docs, 1):
        print(f"\n--- Documento {i} ---")
        print(f"Título: {doc.get('title', 'Sem título')}")
        print(f"Tamanho: {len(doc.get('text', ''))} caracteres")
        metadata = doc.get('metadata', {})
        if metadata:
            print(f"Metadata: {metadata}")

    # Salvar documentos
    print("\n2. Salvando documentos...")
    scraper.save_documents(docs, "exemplo_propaganda.json")
    print("✅ Documentos salvos em data/raw/exemplo_propaganda.json")


def main():
    """Executa todos os exemplos"""
    print("\n" + "=" * 80)
    print("EXEMPLOS DE USO - DJE Análise v2")
    print("=" * 80)

    try:
        # Exemplo 5: Scraper (não requer RAG configurado)
        example_5_scraper_usage()

        # Exemplo 4: Processamento (não requer RAG configurado)
        example_4_document_processing()

        # Exemplos que requerem RAG configurado
        print("\n" + "=" * 80)
        print("Os próximos exemplos requerem o RAG configurado.")
        print("Execute: python main.py --setup")
        print("=" * 80)

        # Descomente após configurar o RAG:
        # example_1_basic_setup()
        # example_2_simple_query()
        # example_3_advanced_query()

    except Exception as e:
        print(f"\n❌ Erro ao executar exemplos: {e}")
        print("\nCertifique-se de:")
        print("1. Configurar a API key da OpenAI no arquivo .env")
        print("2. Instalar todas as dependências: pip install -r requirements.txt")
        print("3. Executar o setup: python main.py --setup")


if __name__ == "__main__":
    main()

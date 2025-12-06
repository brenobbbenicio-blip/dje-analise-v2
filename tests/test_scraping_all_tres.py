"""
Script de teste para verificar raspagem em todos os TREs
"""
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper import DJEScraper
from src.config import AVAILABLE_TRIBUNALS


def test_scraping_all_tribunals():
    """
    Testa a raspagem em todos os tribunais (TSE e TREs)
    """
    print("=" * 80)
    print("🧪 TESTE DE RASPAGEM - TODOS OS TRIBUNAIS")
    print("=" * 80)
    print(f"\nTestando raspagem em {len(AVAILABLE_TRIBUNALS)} tribunais:")
    print(f"  {', '.join(AVAILABLE_TRIBUNALS)}\n")

    results = {}

    for tribunal in AVAILABLE_TRIBUNALS:
        print(f"\n{'='*80}")
        print(f"📋 Testando: {tribunal}")
        print(f"{'='*80}")

        try:
            # Criar scraper com raspagem real habilitada
            scraper = DJEScraper(tribunal=tribunal, use_real_scraping=True)

            # Tentar coletar 1 documento apenas (teste rápido)
            docs = scraper.scrape_search_results(
                search_term="eleições",
                max_results=1
            )

            # Verificar resultado
            if docs and len(docs) > 0:
                results[tribunal] = {
                    'status': 'SUCESSO',
                    'count': len(docs),
                    'source': docs[0]['metadata'].get('source', 'N/A')
                }
                print(f"✅ {tribunal}: Coletou {len(docs)} documento(s)")
            else:
                results[tribunal] = {
                    'status': 'FALHA',
                    'count': 0,
                    'source': 'N/A'
                }
                print(f"⚠️  {tribunal}: Nenhum documento coletado")

        except Exception as e:
            results[tribunal] = {
                'status': 'ERRO',
                'count': 0,
                'source': str(e)[:50]
            }
            print(f"❌ {tribunal}: Erro - {e}")

    # Resumo final
    print("\n" + "=" * 80)
    print("📊 RESUMO DO TESTE")
    print("=" * 80)

    success_count = sum(1 for r in results.values() if r['status'] == 'SUCESSO')

    print(f"\nTotal de tribunais testados: {len(AVAILABLE_TRIBUNALS)}")
    print(f"Raspagem bem-sucedida: {success_count}")
    print(f"Com fallback para exemplos: {len(results) - success_count}")

    print("\n📋 Detalhes por tribunal:")
    print("-" * 80)
    for tribunal, result in results.items():
        status_icon = "✅" if result['status'] == 'SUCESSO' else "📄"
        print(f"{status_icon} {tribunal:10s} | {result['status']:8s} | "
              f"Docs: {result['count']} | {result['source']}")

    print("\n" + "=" * 80)
    print("✅ Teste concluído!")
    print("=" * 80)

    return results


def test_specific_tribunals():
    """
    Testa raspagem em tribunais específicos com mais detalhes
    """
    print("\n" + "=" * 80)
    print("🔍 TESTE DETALHADO - AMOSTRA DE TRIBUNAIS")
    print("=" * 80)

    # Testar alguns tribunais representativos
    sample_tribunals = ["TSE", "TRE-PA", "TRE-MG", "TRE-AM"]

    for tribunal in sample_tribunals:
        print(f"\n{'='*80}")
        print(f"📋 Teste detalhado: {tribunal}")
        print(f"{'='*80}\n")

        try:
            scraper = DJEScraper(tribunal=tribunal, use_real_scraping=True)
            docs = scraper.scrape_search_results(
                search_term="eleições",
                max_results=2
            )

            if docs:
                print(f"\n✅ Coletados {len(docs)} documentos de {tribunal}\n")

                for i, doc in enumerate(docs, 1):
                    print(f"Documento {i}:")
                    print(f"  Título: {doc['title'][:60]}...")
                    print(f"  Texto: {doc['text'][:100]}...")
                    print(f"  Metadados:")
                    for key, value in doc['metadata'].items():
                        print(f"    - {key}: {value}")
                    print()
            else:
                print(f"⚠️  Nenhum documento coletado de {tribunal}")

        except Exception as e:
            print(f"❌ Erro em {tribunal}: {e}")

    print("=" * 80)


if __name__ == "__main__":
    print("\n🚀 Iniciando testes de raspagem...")
    print("⏱️  Este teste pode levar alguns minutos devido aos delays entre requisições.\n")

    # Teste rápido de todos os tribunais
    test_scraping_all_tribunals()

    # Perguntar se quer fazer teste detalhado
    print("\n💡 Deseja executar teste detalhado em tribunais específicos? (s/n): ", end="")
    try:
        if input().lower() == 's':
            test_specific_tribunals()
    except:
        pass

    print("\n✅ Testes finalizados!")

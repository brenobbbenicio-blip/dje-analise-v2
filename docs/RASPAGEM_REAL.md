# 🌐 Guia de Raspagem Real

## 📋 Sobre

O sistema DJE Análise v2 suporta dois modos de operação:

1. **Modo Exemplos** (padrão) - Usa documentos de exemplo pré-configurados
2. **Modo Raspagem Real** (experimental) - Tenta coletar jurisprudência real dos sites dos tribunais

## ✅ Tribunais com Raspagem Implementada

A raspagem real está implementada para **TODOS os 9 tribunais**:

### Nacional
- **TSE** - Tribunal Superior Eleitoral

### Região Norte
- **TRE-PA** - Tribunal Regional Eleitoral do Pará
- **TRE-RO** - Tribunal Regional Eleitoral de Rondônia
- **TRE-AM** - Tribunal Regional Eleitoral do Amazonas
- **TRE-AP** - Tribunal Regional Eleitoral do Amapá

### Região Sudeste
- **TRE-MG** - Tribunal Regional Eleitoral de Minas Gerais
- **TRE-RJ** - Tribunal Regional Eleitoral do Rio de Janeiro

### Região Sul
- **TRE-PR** - Tribunal Regional Eleitoral do Paraná
- **TRE-SC** - Tribunal Regional Eleitoral de Santa Catarina

Cada tribunal possui **padrões de URL específicos** configurados para maximizar as chances de sucesso na raspagem.

## 🚀 Como Usar Raspagem Real

### Setup com Raspagem Real

```bash
# Tentar raspagem real de todos os tribunais
python main.py --setup --scrape

# Raspagem real de tribunais específicos
python main.py --setup --tribunals TSE,TRE-MG --scrape

# Raspagem com mais documentos
python main.py --setup --max-docs 10 --scrape
```

### Como Funciona

O sistema implementa um **fallback inteligente**:

1. ✅ **Tenta raspagem real** do site oficial
2. ⚠️ Se falhar → usa documentos de exemplo
3. 📊 Informa qual método foi usado

## 🔧 Arquitetura Técnica

### Componentes

```
src/scraper/
├── dje_scraper.py        # Scraper principal com lógica de fallback
├── html_parser.py        # Parsers HTML para TSE e TREs
└── example_documents.py  # Documentos de exemplo (fallback)
```

### Parser HTML

O parser tenta múltiplos padrões de HTML:

```python
# Padrões de elementos suportados
- <div class="resultado">
- <article class="jurisprudencia">
- <tr class="linha">
- <li class="item">
```

### URLs Tentadas

Cada tribunal possui padrões de URL específicos configurados em `src/config.py`. Por exemplo:

**TSE:**
```
https://www.tse.jus.br/jurisprudencia/busca?q={termo}
https://www.tse.jus.br/jurisprudencia/jurisprudencia/busca?termo={termo}
https://www.tse.jus.br/jurisprudencia/pesquisa?texto={termo}
https://www.tse.jus.br/jurisprudencia?s={termo}
```

**TREs (Padrão geral):**
```
{base_url}/busca?q={termo}
{base_url}/pesquisa?termo={termo}
{base_url}/consulta?texto={termo}
{base_url}?s={termo}
```

O sistema tenta cada URL sequencialmente até encontrar resultados ou esgotar todas as opções.

## 📊 Metadados

Documentos raspados incluem metadados especiais:

```python
{
    'metadata': {
        'source': 'TSE - Raspagem Real',  # Indica origem
        'number': '123.456',
        'year': 2024,
        'type': 'Acórdão',
        'tema': 'Registro de Candidatura'
    }
}
```

## ⚡ Performance

### Delays

- Entre requisições: 2 segundos (configurável em `src/config.py`)
- Timeout por requisição: 30 segundos
- Retry automático com diferentes URLs

### Headers

User-Agent completo para evitar bloqueios:
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

## ⚠️ Limitações

### Conhecidas

1. **Sites dinâmicos**: Não funciona com JavaScript pesado
2. **CAPTCHAs**: Não suportado (usa fallback)
3. **Rate limiting**: Respeita delays, mas pode ser bloqueado
4. **Estrutura variável**: Cada tribunal tem HTML diferente

### Quando Usar Exemplos

- **Desenvolvimento e testes**
- Sem conexão com internet
- Sites dos tribunais fora do ar
- Demonstrações rápidas

### Quando Usar Raspagem Real

- **Dados atualizados**
- Pesquisa jurídica real
- Produção com monitoramento
- Análise de casos recentes

## 🛠️ Customização

### Adicionar Novos Padrões de URL para um Tribunal

Os padrões de URL são configurados em `src/config.py` dentro de `TRE_CONFIGS`. Para customizar um tribunal específico:

```python
"TRE-PA": {
    "name": "Tribunal Regional Eleitoral do Pará",
    "url": "https://www.tre-pa.jus.br/jurisprudencia",
    "abbreviation": "TRE-PA",
    "state": "PA",
    "search_patterns": [
        "/busca?q={term}",           # Padrão 1
        "/pesquisa?termo={term}",    # Padrão 2
        "/consulta?texto={term}",    # Padrão 3
        "/seu-novo-padrao?x={term}", # Adicione aqui!
        "?s={term}"
    ]
}
```

O scraper tentará cada padrão na ordem até encontrar resultados.

### Melhorar Parser

Edite `src/scraper/html_parser.py`:

```python
# Adicionar novo seletor CSS
items = soup.find_all('div', class_='seu-seletor')
```

### Configurar Timeout

Edite `src/config.py`:

```python
REQUEST_DELAY = 5  # Aumentar delay entre requisições
```

## 📈 Monitoramento

### Logs

O sistema imprime mensagens claras:

```
🌐 Tentando raspagem real do site...
   Tentando URL: https://www.tse.jus.br/busca?q=...
   ✓ Encontrados 5 resultados
✅ Raspagem real bem-sucedida!
```

### Fallback

Quando falha:

```
⚠️  Erro na raspagem real: timeout
📄 Usando documentos de exemplo como fallback...
```

## 🔍 Debugging

### Verificar HTML Retornado

```python
# Em dje_scraper.py, adicione:
print(response.text[:500])  # Primeiros 500 chars
```

### Testar Parser Isoladamente

```python
from src.scraper.html_parser import TSEParser

html = "<div class='resultado'>Teste</div>"
results = TSEParser.parse_search_results(html)
print(results)
```

## 🚧 Desenvolvimento Futuro

### Planejado

- [ ] Suporte a JavaScript (Selenium/Playwright)
- [ ] Cache de requisições
- [ ] Bypass de CAPTCHAs
- [ ] Parser específico por tribunal
- [ ] Download de PDFs de acórdãos
- [ ] Extração de imagens de decisões

### Contribuir

Para melhorar a raspagem:

1. Identifique padrões HTML do tribunal
2. Adicione seletores em `html_parser.py`
3. Teste com `--scrape`
4. Envie PR com melhorias

## 🧪 Testando a Raspagem

### Testar Todos os TREs

Para verificar se a raspagem está funcionando em todos os tribunais:

```bash
python tests/test_scraping_all_tres.py
```

Este script:
- Testa a raspagem em todos os 9 tribunais
- Mostra quais tribunais conseguiram fazer raspagem real
- Indica quais usaram fallback para exemplos
- Fornece um resumo completo dos resultados

### Testar Tribunal Específico

```bash
python main.py --setup --tribunals TRE-PA --scrape --max-docs 2
```

## 📚 Exemplos Práticos

### Exemplo 1: TSE com Raspagem

```bash
python main.py --setup --tribunals TSE --scrape --max-docs 5
```

**Saída esperada:**
```
🔧 Configurando base de dados...
🌐 Modo: RASPAGEM REAL (com fallback para exemplos)
📋 Tribunais selecionados: TSE

📥 Coletando 5 documentos de cada tribunal...
Buscando em TSE - Tribunal Superior Eleitoral
Termo: 'eleições'...
🌐 Tentando raspagem real do site...
   Tentando URL: https://www.tse.jus.br/busca?q=elei...
   ✓ Encontrados 5 resultados
✅ Raspagem real bem-sucedida!
✅ Coletados 5 documentos de TSE
```

### Exemplo 2: Múltiplos TREs

```bash
python main.py --setup --tribunals TRE-MG,TRE-RJ --scrape
```

### Exemplo 3: Fallback Automático

```bash
# Se site estiver fora do ar
python main.py --setup --tribunals TSE --scrape
```

**Saída:**
```
🌐 Tentando raspagem real do site...
⚠️  Erro na raspagem real: Connection timeout
📄 Usando documentos de exemplo como fallback...
✅ Coletados 2 documentos de TSE
```

## 🎓 Boas Práticas

### DO ✅

- Use delays adequados (2-5 segundos)
- Respeite robots.txt dos sites
- Implemente fallback robusto
- Monitore logs para falhas
- Cache resultados quando possível

### DON'T ❌

- Fazer requisições em paralelo descontrolado
- Ignorar códigos de status HTTP
- Fazer scraping 24/7 sem pausa
- Violar termos de uso dos sites
- Sobrecarregar servidores públicos

## 📞 Suporte

Problemas com raspagem?

1. Verifique logs detalhados
2. Teste URLs manualmente no navegador
3. Ajuste parsers para estrutura do site
4. Use modo exemplos como alternativa
5. Abra issue no GitHub com detalhes

---

💡 **Dica**: Para produção, considere usar APIs oficiais quando disponíveis!

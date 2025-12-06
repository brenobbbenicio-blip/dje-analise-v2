# 📚 Exemplos de Uso

Esta pasta contém exemplos práticos de como usar o DJE Análise v2.

## 📋 Arquivos

- `example_usage.py` - Exemplos completos de uso do sistema
- `quick_start.py` - Guia rápido de início

## 🚀 Como Executar

### Preparação

1. Configure o ambiente:
```bash
cp .env.example .env
# Edite .env e adicione sua API key
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o setup inicial:
```bash
python main.py --setup
```

### Executar Exemplos

```bash
# Todos os exemplos
python examples/example_usage.py

# Quick start
python examples/quick_start.py
```

## 📖 O Que Cada Exemplo Demonstra

### Exemplo 1: Configuração Básica
- Como inicializar os componentes
- Como coletar documentos
- Como processar e indexar

### Exemplo 2: Consulta Simples
- Como fazer uma pergunta
- Como obter resposta
- Como acessar as fontes

### Exemplo 3: Consulta Avançada
- Múltiplas perguntas
- Análise de resultados
- Comparação de fontes

### Exemplo 4: Processamento de Documentos
- Como processar textos
- Como criar chunks
- Como adicionar metadata

### Exemplo 5: Uso do Scraper
- Como coletar jurisprudência
- Como salvar documentos
- Como carregar documentos

## 💡 Dicas

- Sempre configure a API key antes de executar
- Use o modo interativo para testes rápidos
- Consulte o README principal para mais detalhes

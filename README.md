# DJE Análise v2

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Sistema avançado de análise de jurisprudência eleitoral com RAG (Retrieval-Augmented Generation). Este sistema permite coletar, processar e realizar buscas semânticas em decisões judiciais eleitorais, utilizando técnicas de processamento de linguagem natural e inteligência artificial.

## 🚀 Funcionalidades

- **Coleta Automatizada**: Scraping de decisões do Diário da Justiça Eletrônica (DJE)
- **Processamento Inteligente**: Análise e fragmentação de textos jurídicos
- **Embeddings Vetoriais**: Geração de embeddings usando OpenAI
- **Busca Semântica**: Busca avançada usando ChromaDB
- **RAG**: Geração de respostas contextualizadas com GPT-4
- **API REST**: Interface completa com FastAPI
- **Docker**: Containerização completa da aplicação

## 📋 Pré-requisitos

- Python 3.11+
- OpenAI API Key
- Docker e Docker Compose (opcional)

## 🔧 Instalação

### Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/brenobbbenicio-blip/dje-analise-v2.git
cd dje-analise-v2
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env e adicione sua OPENAI_API_KEY
```

### Instalação com Docker

1. Clone o repositório e configure o .env:
```bash
git clone https://github.com/brenobbbenicio-blip/dje-analise-v2.git
cd dje-analise-v2
cp .env.example .env
# Edite o .env com sua OPENAI_API_KEY
```

2. Inicie os containers:
```bash
docker-compose up -d
```

## 🎯 Uso

### 1. Coletar Dados do DJE

```bash
python scripts/collect_data.py
```

Este script irá coletar decisões do DJE e salvá-las em `data/raw/`.

### 2. Processar e Indexar Dados

```bash
python scripts/index_data.py
```

Este script processa os dados coletados e indexa no sistema RAG.

### 3. Iniciar a API

```bash
# Modo desenvolvimento
python -m uvicorn src.api.main:app --reload

# Ou usando o script
./scripts/start_api.sh

# Com Docker
docker-compose up
```

A API estará disponível em `http://localhost:8000`

### 4. Acessar a Documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 Endpoints da API

### Health Check
```bash
GET /health
```

### Busca Semântica
```bash
POST /search
Content-Type: application/json

{
  "query": "prestação de contas eleitorais",
  "n_results": 5,
  "filters": {}
}
```

### Consulta com RAG
```bash
POST /query
Content-Type: application/json

{
  "query": "Como funciona a prestação de contas de campanha?",
  "n_results": 5,
  "temperature": 0.7
}
```

### Estatísticas do Sistema
```bash
GET /stats
```

## 📁 Estrutura do Projeto

```
dje-analise-v2/
├── src/
│   ├── api/                 # API REST
│   │   ├── main.py          # Aplicação FastAPI
│   │   └── models.py        # Modelos Pydantic
│   ├── collectors/          # Coletores de dados
│   │   └── dje_collector.py # Coletor do DJE
│   ├── processors/          # Processadores de texto
│   │   └── text_processor.py
│   ├── rag/                 # Sistema RAG
│   │   ├── embeddings.py    # Gerador de embeddings
│   │   ├── vector_store.py  # ChromaDB
│   │   └── rag_system.py    # Sistema completo
│   ├── utils/               # Utilitários
│   │   └── logger.py        # Sistema de logging
│   └── config.py            # Configurações
├── tests/                   # Testes
│   ├── test_api.py
│   └── test_processors.py
├── scripts/                 # Scripts utilitários
│   ├── collect_data.py
│   ├── index_data.py
│   └── start_api.sh
├── data/                    # Dados
│   ├── raw/                 # Dados brutos
│   ├── processed/           # Dados processados
│   └── embeddings/          # Embeddings e ChromaDB
├── docs/                    # Documentação
├── Dockerfile               # Dockerfile
├── docker-compose.yml       # Docker Compose
├── requirements.txt         # Dependências
├── .env.example             # Exemplo de variáveis de ambiente
└── README.md                # Este arquivo
```

## 🧪 Testes

Execute os testes:

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/test_api.py -v
```

## 🔐 Configuração

### Variáveis de Ambiente

Principais variáveis no arquivo `.env`:

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small

# API
API_HOST=0.0.0.0
API_PORT=8000

# RAG
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5

# ChromaDB
COLLECTION_NAME=dje_jurisprudencia
```

## 🏗️ Arquitetura

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   API FastAPI   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────┐   ┌──────────┐
│ RAG │───│ ChromaDB │
└──┬──┘   └──────────┘
   │
   ▼
┌──────────┐
│  OpenAI  │
└──────────┘
```

## 🛠️ Tecnologias

- **FastAPI**: Framework web moderno e de alta performance
- **OpenAI**: GPT-4 para geração de respostas e embeddings
- **ChromaDB**: Banco de dados vetorial para busca semântica
- **LangChain**: Framework para aplicações LLM
- **BeautifulSoup**: Web scraping
- **Pydantic**: Validação de dados
- **Pytest**: Framework de testes

## 📝 Exemplos de Uso

### Python

```python
from src.rag.rag_system import RAGSystem

# Inicializar sistema
rag = RAGSystem()

# Fazer uma consulta
response = rag.generate_response(
    query="Quais são os prazos para prestação de contas?",
    n_results=5
)

print(response['answer'])
print(f"Fontes: {len(response['sources'])}")
```

### cURL

```bash
# Busca
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "eleições municipais", "n_results": 5}'

# Consulta RAG
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Como funciona a prestação de contas?", "n_results": 5}'
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- **DJE Análise Team** - *Trabalho inicial*

## 📞 Suporte

Para suporte, abra uma issue no GitHub ou entre em contato através de [seu-email@example.com](mailto:seu-email@example.com).

## 🗺️ Roadmap

- [ ] Interface web com Streamlit
- [ ] Suporte a mais tribunais
- [ ] Análise de tendências jurisprudenciais
- [ ] Sistema de alertas automáticos
- [ ] Exportação de relatórios
- [ ] Integração com sistemas jurídicos

## 🙏 Agradecimentos

- Tribunal Superior Eleitoral (TSE)
- OpenAI pela API
- Comunidade FastAPI
- Todos os contribuidores

---

**Desenvolvido com ❤️ para o Direito Eleitoral Brasileiro**

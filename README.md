# 🏛️ DJE Análise v2

> Sistema avançado de análise de jurisprudência eleitoral brasileira utilizando RAG (Retrieval-Augmented Generation)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📋 Sobre o Projeto

O **DJE Análise v2** é um sistema inteligente que utiliza técnicas de Inteligência Artificial para análise e consulta de jurisprudência eleitoral brasileira. Através da tecnologia RAG (Retrieval-Augmented Generation), o sistema é capaz de:

- 🔍 Buscar e indexar decisões eleitorais
- 💡 Responder perguntas sobre jurisprudência de forma inteligente
- 📊 Contextualizar respostas com base em documentos reais
- 🎯 Fornecer citações precisas das fontes consultadas

### 🌟 Características

- **RAG Avançado**: Utiliza embeddings e busca vetorial para recuperação de informações relevantes
- **🔍 Detector de Contradições**: IA que identifica automaticamente decisões contraditórias entre tribunais (NOVO!)
- **Cobertura Nacional**: TSE + 8 TREs (Regiões Norte, Sul e Sudeste)
- **Interface CLI**: Interface de linha de comando intuitiva e interativa
- **Processamento Inteligente**: Divisão automática de documentos em chunks otimizados
- **Filtros por Tribunal**: Consulte jurisprudência de tribunais específicos ou por região
- **Fonte Citada**: Todas as respostas incluem referências às decisões consultadas
- **Raspagem Real**: Suporte a coleta direta dos sites dos tribunais (experimental)
- **Extensível**: Arquitetura modular que permite fácil expansão

### 🏛️ Tribunais Suportados

| Tribunal | Sigla | Estado | Região | Status |
|----------|-------|--------|--------|--------|
| Tribunal Superior Eleitoral | TSE | Nacional | - | ✅ Disponível |
| **Região Norte** | | | | |
| TRE Pará | TRE-PA | PA | Norte | ✅ Disponível |
| TRE Amazonas | TRE-AM | AM | Norte | ✅ Disponível |
| TRE Rondônia | TRE-RO | RO | Norte | ✅ Disponível |
| TRE Amapá | TRE-AP | AP | Norte | ✅ Disponível |
| **Região Sul** | | | | |
| TRE Paraná | TRE-PR | PR | Sul | ✅ Disponível |
| TRE Santa Catarina | TRE-SC | SC | Sul | ✅ Disponível |
| **Região Sudeste** | | | | |
| TRE Minas Gerais | TRE-MG | MG | Sudeste | ✅ Disponível |
| TRE Rio de Janeiro | TRE-RJ | RJ | Sudeste | ✅ Disponível |

**Total: 9 tribunais** (1 TSE + 8 TREs cobrindo 3 regiões do Brasil)

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Conta na OpenAI com API key

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/brenobbbenicio-blip/dje-analise-v2.git
cd dje-analise-v2
```

2. **Crie um ambiente virtual (recomendado)**
```bash
python -m venv venv

# No Linux/Mac:
source venv/bin/activate

# No Windows:
venv\Scripts\activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env e adicione sua API key da OpenAI
# OPENAI_API_KEY=sua_chave_api_aqui
```

5. **Configure a base de dados inicial**
```bash
# Coletar de todos os tribunais (TSE + TREs)
python main.py --setup

# Ou apenas de tribunais específicos
python main.py --setup --tribunals TSE,TRE-MG
```

## 💻 Como Usar

### Modo Interativo (Recomendado)

Execute o sistema em modo interativo para fazer múltiplas consultas:

```bash
python main.py --interactive
```

Exemplo de sessão:
```
📝 Digite sua pergunta sobre jurisprudência eleitoral:
> Quais são os requisitos para registro de candidatura?

🔍 Processando consulta...

================================================================================
RESULTADO DA ANÁLISE
================================================================================

Pergunta: Quais são os requisitos para registro de candidatura?

--------------------------------------------------------------------------------

Resposta:
[Resposta gerada pelo sistema com base na jurisprudência]

--------------------------------------------------------------------------------

Fontes consultadas:
1. Acórdão TSE 123.456 - Registro de Candidatura
   Relevância: 0.92
   Número: 123.456
   Ano: 2023
...
```

### Consulta Direta

Para fazer uma consulta única:

```bash
python main.py --query "Qual o prazo para prestação de contas?"
```

### Configuração da Base de Dados

Para reconfigurar a base de dados com mais documentos por tribunal:

```bash
# Mais documentos de cada tribunal
python main.py --setup --max-docs 5

# Apenas tribunais específicos
python main.py --setup --tribunals TRE-MG,TRE-RJ --max-docs 10
```

### Consulta por Tribunal Específico

```bash
# Consulta apenas no TRE-MG
python main.py --query "Requisitos de candidatura" --tribunal TRE-MG

# No modo interativo, use colchetes
python main.py --interactive
> [TRE-RJ] Casos de propaganda eleitoral no Rio
```

### 🔍 Detector de Contradições (NOVO!)

Identifica automaticamente decisões contraditórias entre tribunais usando IA:

```bash
# Detectar contradições sobre um tema
python main.py --detect-contradictions "registro de candidatura"

# Com configurações avançadas
python main.py --detect-contradictions "propaganda eleitoral" \
    --similarity 0.80 \
    --max-cases 100 \
    --export md

# Filtrar por tribunais específicos
python main.py --detect-contradictions "inelegibilidade" \
    --tribunals TRE-MG,TRE-RJ,TRE-SP
```

**O que o detector faz:**
- ✅ Identifica casos similares de tribunais diferentes
- ✅ Detecta decisões opostas (provido vs não provido, etc.)
- ✅ Analisa contradições usando IA (GPT)
- ✅ Classifica gravidade (baixa, média, alta, crítica)
- ✅ Gera relatórios detalhados e acionáveis
- ✅ Exporta para Markdown ou JSON

**Por que é genial:**
- 🚀 Economiza dias de pesquisa manual
- 🎯 Descobre precedentes favoráveis que passariam despercebidos
- ⚖️ Identifica divergências jurisprudenciais automaticamente
- 💡 Fornece recomendações estratégicas para cada contradição

Para documentação completa:
[📚 Guia do Detector de Contradições](docs/DETECTOR_CONTRADICOES.md)

### 🤖 Gerador Automático de Peças Processuais (NOVO!)

Gera petições, recursos e pareceres automaticamente fundamentados em jurisprudência:

```bash
# Gerar recurso eleitoral
python main.py --generate-document recurso \
    --case-description "Candidato teve registro indeferido" \
    --objective "Reformar decisão e deferir registro" \
    --arguments "ausência de inelegibilidade;requisitos cumpridos"

# Gerar petição inicial
python main.py --generate-document petição_inicial \
    --case-description "Propaganda irregular em outdoor" \
    --objective "Aplicação de multa e remoção" \
    --output minha_peticao.txt
```

**Tipos disponíveis:** Petição Inicial, Recurso, Parecer, Impugnação, Contestação

**O que faz:** Redação com IA + Fundamentação em jurisprudência + Estrutura completa + Citações formatadas

**Por que é genial:** ⏱️ Dias → Minutos | 🎯 Sempre fundamentado | 📊 Qualidade profissional

### 🔔 Monitor de Mudanças de Entendimento (NOVO!)

Detecta quando tribunais mudam posicionamento:

```bash
python main.py --monitor-changes "registro de candidatura" --days-back 730
```

**Detecta:** Inversão | Endurecimento | Flexibilização | Divergência
**Por que é genial:** 🔔 Nunca desatualizado | 📈 Tendências | 🚨 Alertas automáticos

## 🎓 Guia de Tribunais

Para um guia completo sobre como usar os múltiplos tribunais, consulte:
[📚 Guia de Uso - Múltiplos Tribunais](docs/GUIA_TRIBUNAIS.md)

## 📁 Estrutura do Projeto

```
dje-analise-v2/
├── src/
│   ├── models/           # Modelos e lógica RAG
│   │   └── rag_system.py
│   ├── scraper/          # Coleta de jurisprudência
│   │   └── dje_scraper.py
│   ├── embeddings/       # Processamento de documentos
│   │   └── document_processor.py
│   ├── utils/            # Funções auxiliares
│   │   └── helpers.py
│   └── config.py         # Configurações do sistema
├── data/
│   ├── raw/              # Documentos brutos coletados
│   ├── processed/        # Documentos processados
│   └── vectorstore/      # Base vetorial ChromaDB
├── docs/                 # Documentação adicional
├── examples/             # Exemplos de uso
├── tests/                # Testes automatizados
├── main.py               # Interface principal
├── requirements.txt      # Dependências Python
├── .env.example          # Exemplo de variáveis de ambiente
└── README.md             # Este arquivo
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Você pode personalizar diversos aspectos do sistema através do arquivo `.env`:

```bash
# Modelo de embeddings (OpenAI)
EMBEDDING_MODEL=text-embedding-3-small

# Modelo de chat (OpenAI)
CHAT_MODEL=gpt-3.5-turbo

# Temperatura do modelo (0.0 a 1.0)
TEMPERATURE=0.3

# Máximo de tokens na resposta
MAX_TOKENS=2000

# Tamanho dos chunks de texto
CHUNK_SIZE=1000

# Sobreposição entre chunks
CHUNK_OVERLAP=200
```

### Personalização do Scraper

Edite `src/config.py` para ajustar:
- URL base do TSE
- Delay entre requisições
- Número máximo de documentos por busca

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para mais detalhes.

## 📝 Exemplos de Perguntas

O sistema pode responder diversos tipos de perguntas sobre jurisprudência eleitoral:

- "Quais são os requisitos para registro de candidatura?"
- "O que configura abuso de poder econômico?"
- "Qual o prazo para prestação de contas de campanha?"
- "Quais são as causas de inelegibilidade?"
- "Como funciona a propaganda eleitoral na internet?"

## 🔒 Segurança

- Nunca compartilhe sua API key da OpenAI publicamente
- O arquivo `.env` está no `.gitignore` para evitar commits acidentais
- Revise sempre os documentos antes de adicioná-los à base

## 🐛 Problemas Conhecidos

- O scraper atual usa documentos de exemplo (implementação completa depende da estrutura do site do TSE)
- Requisitos de API key da OpenAI (custo por uso)

## 📚 Documentação Adicional

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [LangChain Documentation](https://python.langchain.com/)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- **Breno Benicio** - *Desenvolvimento inicial* - [@brenobbbenicio-blip](https://github.com/brenobbbenicio-blip)

## 🙏 Agradecimentos

- TSE (Tribunal Superior Eleitoral) pela disponibilização da jurisprudência
- Comunidade OpenAI
- Contribuidores do projeto

## 📞 Contato

Para dúvidas, sugestões ou problemas, abra uma [issue](https://github.com/brenobbbenicio-blip/dje-analise-v2/issues) no GitHub.

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!

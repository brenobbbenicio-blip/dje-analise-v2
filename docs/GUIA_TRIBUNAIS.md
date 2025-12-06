# 📚 Guia de Uso - Múltiplos Tribunais

Este guia explica como usar o sistema DJE Análise v2 com múltiplos Tribunais Regionais Eleitorais.

## 🏛️ Tribunais Disponíveis

O sistema agora suporta:

- **TSE** - Tribunal Superior Eleitoral (Nacional)
- **TRE-MG** - Tribunal Regional Eleitoral de Minas Gerais
- **TRE-RJ** - Tribunal Regional Eleitoral do Rio de Janeiro
- **TRE-PR** - Tribunal Regional Eleitoral do Paraná
- **TRE-SC** - Tribunal Regional Eleitoral de Santa Catarina

## 🚀 Configuração da Base de Dados

### Setup Completo (Todos os Tribunais)

Coletar documentos de todos os tribunais disponíveis:

```bash
python main.py --setup
```

Isso coletará 2 documentos de cada tribunal por padrão.

### Setup com Mais Documentos

Para coletar mais documentos de cada tribunal:

```bash
python main.py --setup --max-docs 5
```

### Setup de Tribunais Específicos

Para coletar apenas de tribunais selecionados:

```bash
# Apenas TSE e TRE-MG
python main.py --setup --tribunals TSE,TRE-MG

# Apenas TREs do Sul/Sudeste
python main.py --setup --tribunals TRE-RJ,TRE-PR,TRE-SC
```

## 🔍 Consultando a Jurisprudência

### Consulta em Todos os Tribunais

Por padrão, as consultas buscam em todos os tribunais:

```bash
python main.py --query "Quais são os requisitos para registro de candidatura?"
```

### Consulta em Tribunal Específico

#### Via Linha de Comando

```bash
python main.py --query "Requisitos de candidatura" --tribunal TRE-MG
```

#### Modo Interativo

No modo interativo, use colchetes para filtrar por tribunal:

```bash
python main.py --interactive
```

Exemplos de consultas no modo interativo:

```
> Quais os requisitos para candidatura?
(busca em todos os tribunais)

> [TRE-MG] Quais os requisitos para candidatura em Minas Gerais?
(busca apenas no TRE-MG)

> [TSE] O que diz a jurisprudência sobre propaganda eleitoral?
(busca apenas no TSE)

> [TRE-RJ] Casos de abuso de poder no Rio de Janeiro
(busca apenas no TRE-RJ)
```

## 📊 Visualizar Estatísticas

### Modo Interativo

Ao iniciar o modo interativo, você verá a distribuição de documentos:

```
📊 Base de dados: 10 documentos

   Distribuição por tribunal:
   - TSE: 2 documentos
   - TRE-MG: 2 documentos
   - TRE-RJ: 2 documentos
   - TRE-PR: 2 documentos
   - TRE-SC: 2 documentos
```

## 💡 Exemplos Práticos

### Exemplo 1: Comparar Jurisprudência Entre Estados

```python
# Setup com estados específicos
python main.py --setup --tribunals TRE-MG,TRE-RJ,TRE-SP

# Consultar em cada estado
python main.py --query "Propaganda em redes sociais" --tribunal TRE-MG
python main.py --query "Propaganda em redes sociais" --tribunal TRE-RJ
python main.py --query "Propaganda em redes sociais" --tribunal TRE-SP
```

### Exemplo 2: Análise Regional

```bash
# Coletar apenas de TREs do Sudeste
python main.py --setup --tribunals TRE-MG,TRE-RJ --max-docs 5

# Consultar na jurisprudência regional
python main.py --interactive

> [TRE-MG] Casos de registro de candidatura em Belo Horizonte
> [TRE-RJ] Casos de prestação de contas no Rio de Janeiro
```

### Exemplo 3: Visão Nacional + Regional

```bash
# Setup completo
python main.py --setup --max-docs 3

# Comparar TSE com TRE específico
python main.py --interactive

> Inelegibilidade por rejeição de contas
(mostra jurisprudência de todos os tribunais)

> [TSE] Inelegibilidade por rejeição de contas
(mostra apenas jurisprudência do TSE)

> [TRE-SC] Inelegibilidade por rejeição de contas
(mostra apenas jurisprudência do TRE-SC)
```

## 🎯 Casos de Uso

### 1. Advogado Eleitoral

Um advogado em Minas Gerais pode:

```bash
# Configurar com TSE + TRE-MG
python main.py --setup --tribunals TSE,TRE-MG --max-docs 10

# Consultar jurisprudência local
python main.py --interactive
> [TRE-MG] Casos de impugnação de candidatura em Uberlândia
```

### 2. Pesquisador Acadêmico

Um pesquisador comparando jurisprudência regional:

```bash
# Coletar de todos os TREs
python main.py --setup --max-docs 20

# Analisar diferenças regionais
> [TRE-MG] Abuso de poder econômico
> [TRE-RJ] Abuso de poder econômico
> [TRE-PR] Abuso de poder econômico
```

### 3. Candidato a Cargo Público

Um candidato verificando requisitos:

```bash
# Setup regional
python main.py --setup --tribunals TSE,TRE-PR

# Consultar requisitos
> Quais documentos preciso para registro de candidatura?
> [TRE-PR] Requisitos específicos para candidatura no Paraná
```

## 📈 Dicas de Uso

1. **Comece com TSE**: O TSE tem jurisprudência de âmbito nacional
   ```bash
   python main.py --setup --tribunals TSE
   ```

2. **Adicione seu estado**: Depois adicione o TRE do seu estado
   ```bash
   python main.py --setup --tribunals TSE,TRE-MG
   ```

3. **Use filtros estrategicamente**:
   - Sem filtro: visão geral
   - Com filtro: casos específicos do tribunal

4. **Combine consultas**: Compare TSE com TRE local para ver alinhamento

## 🔧 Parâmetros Disponíveis

| Parâmetro | Descrição | Exemplo |
|-----------|-----------|---------|
| `--setup` | Configura base de dados | `--setup` |
| `--max-docs` | Docs por tribunal | `--max-docs 5` |
| `--tribunals` | Tribunais a coletar | `--tribunals TSE,TRE-MG` |
| `--query` | Consulta direta | `--query "pergunta"` |
| `--tribunal` | Filtrar tribunal | `--tribunal TRE-MG` |
| `--interactive` | Modo interativo | `--interactive` |

## ❓ Perguntas Frequentes

**P: Posso adicionar mais tribunais depois?**
R: Sim! Execute `--setup --tribunals NOVO_TRE` para adicionar.

**P: Como limpar e recomeçar?**
R: Delete a pasta `data/vectorstore` e execute setup novamente.

**P: Quantos documentos devo coletar?**
R: Para testes: 2-5. Para uso profissional: 10-20+.

**P: Os tribunais têm jurisprudência diferente?**
R: Sim! TREs julgam casos regionais, TSE julga casos nacionais.

## 🎓 Próximos Passos

1. Experimente com diferentes tribunais
2. Compare jurisprudência entre estados
3. Analise diferenças regionais
4. Contribua com melhorias no GitHub

---

💡 **Dica Final**: Use o modo interativo para explorar. É mais intuitivo e permite testar rapidamente diferentes tribunais!

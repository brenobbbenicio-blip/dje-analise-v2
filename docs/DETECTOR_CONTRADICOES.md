# 🔍 Detector de Contradições Jurisprudenciais

## 📋 Visão Geral

O **Detector de Contradições Jurisprudenciais** é uma funcionalidade avançada que usa Inteligência Artificial para identificar automaticamente quando diferentes tribunais eleitorais decidem de forma contraditória sobre casos similares.

### 🎯 Problema que Resolve

Advogados e profissionais do direito gastam dias pesquisando manualmente jurisprudências, tentando identificar:
- Decisões contraditórias entre tribunais
- Divergências jurisprudenciais sobre o mesmo tema
- Precedentes favoráveis que passam despercebidos
- Mudanças de entendimento ao longo do tempo

### ✨ Solução

Este sistema automatiza completamente esse processo usando:
- **Análise semântica** com embeddings de IA
- **Comparação inteligente** entre decisões de tribunais diferentes
- **Detecção de padrões** contraditórios
- **Geração de relatórios** detalhados e acionáveis

## 🚀 Como Usar

### Uso Básico

```bash
# Detectar contradições sobre um tema
python main.py --detect-contradictions "registro de candidatura"
```

### Uso Avançado

```bash
# Com limiar de similaridade customizado (75% de similaridade)
python main.py --detect-contradictions "propaganda eleitoral" --similarity 0.75

# Analisando mais casos (até 100)
python main.py --detect-contradictions "fake news" --max-cases 100

# Filtrar por tribunais específicos
python main.py --detect-contradictions "inelegibilidade" --tribunals TRE-MG,TRE-RJ,TRE-SP

# Exportar relatório em Markdown
python main.py --detect-contradictions "abuso de poder" --export md

# Exportar em JSON para análise programática
python main.py --detect-contradictions "direitos políticos" --export json
```

## 📊 Como Funciona

### 1. Busca Semântica

O sistema busca casos relevantes na base de dados usando embeddings (representações vetoriais) da sua consulta:

```
Consulta: "registro de candidatura"
        ↓
    Embedding
        ↓
  Busca no ChromaDB
        ↓
50 casos mais relevantes
```

### 2. Identificação de Pares Similares

Compara cada par de casos de tribunais diferentes:

```python
TRE-MG: Acórdão sobre registro
    vs
TRE-RJ: Acórdão sobre registro
    ↓
Similaridade: 87%  ✅ (acima do limiar)
```

### 3. Detecção de Contradição

Para cada par similar, o sistema:

1. **Extrai a decisão** de cada caso:
   - Provido / Não provido
   - Procedente / Improcedente
   - Deferido / Indeferido

2. **Verifica oposição**: Se as decisões são opostas

3. **Análise profunda com IA**: GPT analisa o conteúdo completo e determina:
   - Se realmente há contradição
   - Tipo da contradição
   - Gravidade (baixa, média, alta, crítica)
   - Impacto jurídico
   - Recomendação estratégica

### 4. Agrupamento e Relatório

Contradições são agrupadas por tema e apresentadas em relatório estruturado.

## 📋 Tipos de Contradição

O sistema identifica 4 tipos:

### 1. Decisão Oposta
Casos similares com resultados opostos.

**Exemplo:**
- TRE-MG: Recurso **provido** para deferir registro
- TRE-RJ: Recurso **não provido** em caso idêntico

### 2. Fundamento Diverso
Mesmo resultado, mas fundamentação jurídica contraditória.

**Exemplo:**
- TRE-PA: Inelegibilidade aplicada por interpretação X
- TRE-AM: Inelegibilidade não aplicada por interpretação Y contrária

### 3. Interpretação Divergente
Interpretações diferentes da mesma lei.

**Exemplo:**
- TSE: Interpreta Lei Complementar de forma literal
- TRE-MG: Interpreta mesma lei de forma extensiva

### 4. Critério Conflitante
Critérios de julgamento incompatíveis.

**Exemplo:**
- TRE-PR: Usa critério objetivo para abuso de poder
- TRE-SC: Usa critério subjetivo no mesmo contexto

## 🎚️ Níveis de Gravidade

### Baixa 📘
Contradição menor, sem grande impacto prático.

### Média ⚠️
Contradição relevante que merece atenção.

### Alta 🔴
Contradição significativa que pode afetar estratégia processual.

### Crítica 🚨
Contradição grave com alto impacto jurídico - **requer ação imediata**.

## 📄 Formato do Relatório

### Terminal

O relatório no terminal inclui:

```
🔍 RELATÓRIO DE ANÁLISE DE CONTRADIÇÕES JURISPRUDENCIAIS
====================================================================

📅 Gerado em: 06/12/2025 às 14:30:00
🔎 Consulta: registro de candidatura
📊 Casos analisados: 45
⚠️  Contradições encontradas: 7

🌟 PRINCIPAIS DESCOBERTAS
====================================================================
  🚨 2 contradição(ões) CRÍTICA(S) detectada(s)
  ⚠️  Tema 'Registro de Candidatura' é o mais problemático
  📊 TRE-MG aparece em 4 contradição(ões)

🚨 CONTRADIÇÕES CRÍTICAS - ATENÇÃO URGENTE
====================================================================

🚨 CONTRADIÇÃO #1 - Gravidade: CRÍTICA
────────────────────────────────────────────────────────────────
🔹 Tipo: Decisão Oposta
🔹 Similaridade: 92.3%

📋 CASO 1: TRE-MG
   Acórdão TRE-MG 12345 - Registro deferido
   Decisão: deferido

📋 CASO 2: TRE-RJ
   Acórdão TRE-RJ 67890 - Registro indeferido
   Decisão: indeferido

💭 ANÁLISE:
   Casos praticamente idênticos sobre filiação partidária, mas
   com decisões diametralmente opostas. TRE-MG aplicou prazo de
   6 meses, TRE-RJ aplicou 1 ano.

⚖️  IMPACTO JURÍDICO:
   Alta divergência jurisprudencial pode ensejar recurso especial
   para uniformização de entendimento.

💡 RECOMENDAÇÃO:
   Utilize precedente do TRE-MG se favorável. Argua divergência
   jurisprudencial em recurso.

[...]
```

### Markdown Export

```markdown
# 🔍 Relatório de Análise de Contradições Jurisprudenciais

**Gerado em:** 06/12/2025 às 14:30:00
**Consulta:** registro de candidatura
**Casos analisados:** 45
**Contradições encontradas:** 7

## 🌟 Principais Descobertas

- 🚨 2 contradição(ões) CRÍTICA(S) detectada(s)
- ⚠️ Tema 'Registro de Candidatura' é o mais problemático
[...]
```

### JSON Export

```json
{
  "metadata": {
    "generated_at": "2025-12-06T14:30:00",
    "query": "registro de candidatura",
    "total_cases_analyzed": 45,
    "contradictions_found": 7
  },
  "contradictions": [
    {
      "id": "uuid-123",
      "type": "decisao_oposta",
      "severity": "crítica",
      "similarity": 0.923,
      "case1": {...},
      "case2": {...},
      "explanation": "...",
      "legal_impact": "...",
      "recommended_action": "..."
    }
  ]
}
```

## 🎛️ Parâmetros de Configuração

### --similarity (0.0 a 1.0)

Controla quão similares os casos devem ser para serem comparados.

- **0.5 - 0.7**: Amplo - captura muitas comparações, pode ter falsos positivos
- **0.75** (padrão): Equilibrado - boa precisão
- **0.8 - 0.9**: Restrito - alta precisão, pode perder alguns casos
- **0.9 - 1.0**: Muito restrito - apenas casos quase idênticos

**Recomendação:** Use 0.75 para análise geral, 0.85+ para casos muito específicos.

### --max-cases

Número máximo de casos a analisar.

- **20-30**: Análise rápida
- **50** (padrão): Análise completa
- **100+**: Análise exaustiva (mais lenta)

**Recomendação:** 50 é ideal para a maioria dos casos.

### --tribunals

Filtrar por tribunais específicos.

```bash
# Apenas região Sudeste
--tribunals TRE-MG,TRE-RJ,TRE-SP,TRE-ES

# Comparar TSE com TREs
--tribunals TSE,TRE-PA,TRE-AM
```

## 💡 Casos de Uso

### 1. Pesquisa Jurídica Inicial

```bash
# Antes de protocolar uma petição, verificar se há contradições
python main.py --detect-contradictions "seu tema" --export md
```

**Benefício:** Descobre precedentes favoráveis e desfavoráveis em minutos.

### 2. Preparação de Recursos

```bash
# Identificar divergências para argumentar em recurso
python main.py --detect-contradictions "tema do recurso" --similarity 0.8
```

**Benefício:** Fundamentação robusta com precedentes contraditórios.

### 3. Monitoramento Jurisprudencial

```bash
# Verificar periodicamente mudanças de entendimento
python main.py --detect-contradictions "tema importante" --max-cases 100
```

**Benefício:** Nunca fica desatualizado sobre viradas jurisprudenciais.

### 4. Análise Comparativa Regional

```bash
# Ver como diferentes estados decidem
python main.py --detect-contradictions "fake news" --tribunals TRE-PA,TRE-AM,TRE-RO,TRE-AP
```

**Benefício:** Identifica padrões regionais de julgamento.

### 5. Exportação para Relatórios

```bash
# Gerar relatório para cliente ou equipe
python main.py --detect-contradictions "abuso de poder" --export md
```

**Benefício:** Relatório profissional pronto para compartilhar.

## 🔧 Arquitetura Técnica

### Componentes

```
ContradictionDetector
├── _fetch_relevant_cases()     # Busca semântica com embeddings
├── _find_similar_pairs()        # Comparação n×n otimizada
├── _detect_decision_type()      # Regex para extrair decisão
├── _calculate_similarity()      # Cosine similarity
├── _check_contradiction()       # Verificação de oposição
├── _ai_contradiction_analysis() # Análise profunda com GPT
├── _cluster_contradictions()    # Agrupamento temático
└── create_alerts()              # Geração de alertas
```

### Modelos de Dados

```python
@dataclass
class Contradiction:
    id: str
    case1: JurisprudenceCase
    case2: JurisprudenceCase
    similarity_score: float
    contradiction_type: str
    contradiction_severity: str
    explanation: str
    legal_impact: str
    recommended_action: str
```

### Fluxo de Processamento

```
Query
  ↓
Embedding (OpenAI)
  ↓
Busca no ChromaDB (top 50)
  ↓
Comparação de pares (n×n)
  ↓
Filtro por similaridade (>= 0.75)
  ↓
Detecção de decisões opostas
  ↓
Análise de contradição (GPT)
  ↓
Agrupamento temático
  ↓
Geração de relatório
  ↓
Exportação (opcional)
```

## 📈 Performance

### Complexidade

- **Busca inicial:** O(1) - busca vetorial otimizada
- **Comparação de pares:** O(n²) - otimizado com threshold
- **Análise IA:** O(k) - apenas para pares contraditórios

### Tempo de Execução

- **50 casos:** ~30-60 segundos
- **100 casos:** ~2-4 minutos
- **Limitado por:** Chamadas à API da OpenAI

### Custos (OpenAI API)

- **Embeddings:** ~$0.0001 por documento
- **Análise GPT:** ~$0.002 por contradição detectada
- **50 casos típicos:** ~$0.05 - $0.15

## 🎯 Melhores Práticas

### ✅ Faça

1. **Use consultas específicas**: "registro de candidatura por filiação" > "registro"
2. **Ajuste similarity**: Comece com 0.75, refine conforme necessário
3. **Exporte relatórios**: Mantenha histórico para referência futura
4. **Analise críticas primeiro**: Foque em contradições críticas e altas
5. **Compare regiões**: Use --tribunals para análises regionais

### ❌ Evite

1. **Consultas genéricas demais**: "eleições" retorna muitos falsos positivos
2. **Similarity muito baixo**: < 0.6 gera muitos falsos positivos
3. **Ignorar contexto**: Leia os casos completos, não apenas o resumo
4. **Confiar cegamente**: IA pode errar, sempre valide análises críticas

## 🚨 Limitações

### 1. Base de Dados

Só detecta contradições nos documentos já coletados. Execute `--setup` regularmente.

### 2. Similaridade Semântica

Casos similares semanticamente podem ser juridicamente diferentes. Sempre valide.

### 3. Detecção de Decisão

Regex pode não capturar todas as variações de redação. Sistema está em evolução.

### 4. Análise IA

GPT pode ocasionalmente interpretar incorretamente. Contradições críticas sempre devem ser validadas manualmente.

### 5. Tribunais Disponíveis

Atualmente limitado aos 9 tribunais configurados (TSE + 8 TREs).

## 🔮 Desenvolvimentos Futuros

### Planejado

- [ ] Detecção de mudança de entendimento ao longo do tempo
- [ ] Análise de perfil de magistrados (quem tende a decidir como)
- [ ] Predição de resultados baseada em contradições históricas
- [ ] Alertas automáticos via email/webhook
- [ ] Integração com calendário processual
- [ ] Visualização gráfica de contradições (grafos)
- [ ] Análise de votos (maioria vs minoria)
- [ ] Exportação para PDF formatado

## 📚 Exemplos Práticos

### Exemplo 1: Pesquisa Básica

```bash
$ python main.py --detect-contradictions "propaganda eleitoral"

🔍 Iniciando análise de contradições para: 'propaganda eleitoral'
   Limiar de similaridade: 75.00%
   Máximo de casos: 50

📋 Encontrados 42 casos relevantes
🔗 Identificados 18 pares de casos similares
⚠️  Detectadas 5 contradições

📊 Agrupadas em 3 clusters temáticos

✅ Análise concluída!

[Relatório completo exibido...]
```

### Exemplo 2: Análise Regional

```bash
$ python main.py --detect-contradictions "fake news" \
    --tribunals TRE-PA,TRE-RO,TRE-AM,TRE-AP \
    --export md

📊 Base de dados: 127 documentos

🔍 Iniciando análise de contradições para: 'fake news'
[...]

✅ Relatório exportado para: data/processed/contradictions_20251206_143000.md
```

### Exemplo 3: Análise Profunda

```bash
$ python main.py --detect-contradictions "abuso de poder econômico" \
    --similarity 0.85 \
    --max-cases 100 \
    --export json

[Análise detalhada com 100 casos...]

✅ Relatório JSON exportado para: data/processed/contradictions_20251206_143500.json
```

## 🤝 Contribuindo

Ajude a melhorar o detector:

1. Reporte bugs e casos de falsos positivos/negativos
2. Sugira novos padrões de detecção de decisão
3. Contribua com parsers específicos para tribunais
4. Compartilhe casos de uso interessantes

## 📞 Suporte

Encontrou um problema? Tem uma sugestão?

- GitHub Issues: [github.com/seu-usuario/dje-analise-v2/issues](https://github.com)
- Documentação: [docs/](.)
- Exemplos: [tests/test_contradiction_detector.py](../tests/)

---

**Criado com IA 🤖 para revolucionar a pesquisa jurídica ⚖️**

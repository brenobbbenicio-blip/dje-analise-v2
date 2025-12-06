"""
Detector de Contradições Jurisprudenciais
Identifica automaticamente decisões contraditórias entre tribunais
"""
import re
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import defaultdict

import openai
from chromadb.api.models.Collection import Collection

from ..models.contradiction_models import (
    JurisprudenceCase,
    SimilarCase,
    Contradiction,
    ContradictionCluster,
    ContradictionReport,
    ContradictionAlert
)
from ..config import OPENAI_API_KEY, CHAT_MODEL


class ContradictionDetector:
    """
    Detector avançado de contradições jurisprudenciais
    """

    def __init__(self, collection: Collection):
        """
        Inicializa o detector

        Args:
            collection: Coleção ChromaDB com jurisprudências
        """
        self.collection = collection
        openai.api_key = OPENAI_API_KEY

        # Padrões de decisão
        self.decision_patterns = {
            'provido': r'\b(provid[oa]|deu-se provimento|dar provimento)\b',
            'nao_provido': r'\b(n[ãa]o[- ]provid[oa]|negou-se provimento|negar provimento|desprovid[oa])\b',
            'procedente': r'\b(procedente|acolh\w+)\b',
            'improcedente': r'\b(improcedente|rejeit\w+)\b',
            'deferido': r'\b(deferid[oa]|defere-se)\b',
            'indeferido': r'\b(indeferid[oa]|indefere-se)\b',
        }

    def detect_contradictions(
        self,
        query: str,
        similarity_threshold: float = 0.75,
        max_cases: int = 50,
        tribunal_filter: Optional[List[str]] = None
    ) -> ContradictionReport:
        """
        Detecta contradições para uma consulta específica

        Args:
            query: Consulta/tema para análise
            similarity_threshold: Limiar de similaridade (0.0 a 1.0)
            max_cases: Número máximo de casos a analisar
            tribunal_filter: Lista de tribunais para filtrar (None = todos)

        Returns:
            Relatório completo de contradições
        """
        print(f"\n🔍 Iniciando análise de contradições para: '{query}'")
        print(f"   Limiar de similaridade: {similarity_threshold:.2%}")
        print(f"   Máximo de casos: {max_cases}")

        # 1. Buscar casos relevantes
        cases = self._fetch_relevant_cases(query, max_cases, tribunal_filter)
        print(f"\n📋 Encontrados {len(cases)} casos relevantes")

        if len(cases) < 2:
            print("⚠️  Poucos casos encontrados para análise de contradições")
            return self._create_empty_report(query, len(cases))

        # 2. Identificar pares de casos similares
        similar_pairs = self._find_similar_pairs(cases, similarity_threshold)
        print(f"🔗 Identificados {len(similar_pairs)} pares de casos similares")

        # 3. Analisar contradições
        contradictions = self._analyze_contradictions(similar_pairs)
        print(f"⚠️  Detectadas {len(contradictions)} contradições")

        # 4. Agrupar por tema
        clusters = self._cluster_contradictions(contradictions)
        print(f"📊 Agrupadas em {len(clusters)} clusters temáticos")

        # 5. Gerar estatísticas
        tribunal_stats = self._calculate_tribunal_statistics(cases, contradictions)

        # 6. Gerar highlights e recomendações
        highlights = self._generate_highlights(contradictions, clusters)
        recommendations = self._generate_recommendations(contradictions, clusters)

        # 7. Criar relatório
        report = ContradictionReport(
            generated_at=datetime.now(),
            query=query,
            total_cases_analyzed=len(cases),
            contradictions_found=len(contradictions),
            clusters=clusters,
            tribunal_comparison=tribunal_stats,
            highlights=highlights,
            recommendations=recommendations
        )

        print(f"\n✅ Análise concluída!")
        return report

    def _fetch_relevant_cases(
        self,
        query: str,
        max_results: int,
        tribunal_filter: Optional[List[str]] = None
    ) -> List[JurisprudenceCase]:
        """Busca casos relevantes na base de dados"""
        # Criar embedding da query
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding

        # Buscar no ChromaDB
        where_filter = None
        if tribunal_filter:
            where_filter = {"tribunal": {"$in": tribunal_filter}}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=max_results,
            where=where_filter,
            include=['documents', 'metadatas', 'distances']
        )

        # Converter para JurisprudenceCase
        cases = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                case = JurisprudenceCase(
                    id=results['ids'][0][i],
                    title=metadata.get('title', 'Sem título'),
                    text=doc,
                    tribunal=metadata.get('tribunal', 'N/A'),
                    tribunal_name=metadata.get('tribunal_name', 'N/A'),
                    number=metadata.get('number'),
                    year=metadata.get('year'),
                    tema=metadata.get('tema'),
                    metadata=metadata
                )
                # Detectar tipo de decisão
                case.decision_type = self._detect_decision_type(doc)
                cases.append(case)

        return cases

    def _detect_decision_type(self, text: str) -> Optional[str]:
        """Detecta o tipo de decisão no texto"""
        text_lower = text.lower()

        for decision_type, pattern in self.decision_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return decision_type

        return None

    def _find_similar_pairs(
        self,
        cases: List[JurisprudenceCase],
        threshold: float
    ) -> List[SimilarCase]:
        """Encontra pares de casos similares de tribunais diferentes"""
        similar_pairs = []

        # Comparar cada par de casos
        for i, case1 in enumerate(cases):
            for case2 in cases[i+1:]:
                # Apenas comparar casos de tribunais diferentes
                if case1.tribunal == case2.tribunal:
                    continue

                # Calcular similaridade
                similarity = self._calculate_similarity(case1, case2)

                if similarity >= threshold:
                    similar_pairs.append(SimilarCase(
                        case1=case1,
                        case2=case2,
                        similarity_score=similarity,
                        semantic_distance=1 - similarity
                    ))

        # Ordenar por similaridade (maior primeiro)
        similar_pairs.sort(key=lambda x: x.similarity_score, reverse=True)

        return similar_pairs

    def _calculate_similarity(
        self,
        case1: JurisprudenceCase,
        case2: JurisprudenceCase
    ) -> float:
        """
        Calcula similaridade entre dois casos
        Usa embeddings + comparação de metadados
        """
        # Criar embeddings
        texts = [case1.text[:1000], case2.text[:1000]]  # Limitar tamanho
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )

        emb1 = response.data[0].embedding
        emb2 = response.data[1].embedding

        # Calcular similaridade de cosseno
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = sum(a * a for a in emb1) ** 0.5
        norm2 = sum(b * b for b in emb2) ** 0.5
        cosine_similarity = dot_product / (norm1 * norm2)

        # Boost se mesmo tema
        if case1.tema and case2.tema and case1.tema == case2.tema:
            cosine_similarity = min(1.0, cosine_similarity * 1.1)

        return max(0.0, min(1.0, cosine_similarity))

    def _analyze_contradictions(
        self,
        similar_pairs: List[SimilarCase]
    ) -> List[Contradiction]:
        """Analisa pares similares para detectar contradições"""
        contradictions = []

        print(f"\n🔍 Analisando {len(similar_pairs)} pares similares...")

        for pair in similar_pairs:
            contradiction = self._check_contradiction(pair)
            if contradiction:
                contradictions.append(contradiction)

        return contradictions

    def _check_contradiction(self, pair: SimilarCase) -> Optional[Contradiction]:
        """
        Verifica se um par de casos similares contém contradição
        Usa IA para análise profunda
        """
        case1 = pair.case1
        case2 = pair.case2

        # Verificação rápida: decisões opostas?
        if self._has_opposite_decisions(case1.decision_type, case2.decision_type):
            # Análise profunda com IA
            analysis = self._ai_contradiction_analysis(case1, case2)

            if analysis['is_contradiction']:
                contradiction = Contradiction(
                    id=str(uuid.uuid4()),
                    case1=case1,
                    case2=case2,
                    similarity_score=pair.similarity_score,
                    contradiction_type=analysis['type'],
                    contradiction_severity=analysis['severity'],
                    explanation=analysis['explanation'],
                    legal_impact=analysis['legal_impact'],
                    recommended_action=analysis['recommendation']
                )
                return contradiction

        return None

    def _has_opposite_decisions(self, decision1: Optional[str], decision2: Optional[str]) -> bool:
        """Verifica se duas decisões são opostas"""
        if not decision1 or not decision2:
            return False

        opposites = [
            {'provido', 'nao_provido'},
            {'procedente', 'improcedente'},
            {'deferido', 'indeferido'}
        ]

        for opposite_pair in opposites:
            if {decision1, decision2} == opposite_pair:
                return True

        return False

    def _ai_contradiction_analysis(
        self,
        case1: JurisprudenceCase,
        case2: JurisprudenceCase
    ) -> Dict:
        """
        Usa IA para análise profunda de contradição
        """
        prompt = f"""Você é um especialista em análise jurisprudencial. Analise se há contradição entre estas duas decisões:

CASO 1 ({case1.tribunal_name}):
Título: {case1.title}
Decisão: {case1.decision_type or 'não detectada'}
Texto: {case1.text[:800]}...

CASO 2 ({case2.tribunal_name}):
Título: {case2.title}
Decisão: {case2.decision_type or 'não detectada'}
Texto: {case2.text[:800]}...

Responda em formato JSON:
{{
  "is_contradiction": true/false,
  "type": "decisao_oposta" | "fundamento_diverso" | "interpretacao_divergente" | "criterio_conflitante",
  "severity": "baixa" | "média" | "alta" | "crítica",
  "explanation": "Explicação clara da contradição em 2-3 frases",
  "legal_impact": "Impacto jurídico desta contradição",
  "recommendation": "Recomendação estratégica para advogados"
}}"""

        try:
            response = openai.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise jurisprudencial eleitoral brasileira."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"⚠️  Erro na análise IA: {e}")
            # Fallback: análise básica
            return {
                "is_contradiction": True,
                "type": "decisao_oposta",
                "severity": "média",
                "explanation": f"Decisões opostas detectadas: {case1.tribunal} vs {case2.tribunal}",
                "legal_impact": "Possível divergência jurisprudencial entre tribunais",
                "recommendation": "Verificar qual entendimento é mais recente e fundamentado"
            }

    def _cluster_contradictions(
        self,
        contradictions: List[Contradiction]
    ) -> List[ContradictionCluster]:
        """Agrupa contradições por tema"""
        # Agrupar por tema
        theme_groups = defaultdict(list)

        for contradiction in contradictions:
            # Usar tema do caso 1 ou caso 2
            theme = (contradiction.case1.tema or
                    contradiction.case2.tema or
                    "Tema não especificado")
            theme_groups[theme].append(contradiction)

        # Criar clusters
        clusters = []
        for theme, group_contradictions in theme_groups.items():
            # Tribunais afetados
            tribunals = set()
            for c in group_contradictions:
                tribunals.add(c.case1.tribunal)
                tribunals.add(c.case2.tribunal)

            # Distribuição de gravidade
            severity_dist = defaultdict(int)
            for c in group_contradictions:
                severity_dist[c.contradiction_severity] += 1

            # Gerar resumo
            summary = self._generate_cluster_summary(theme, group_contradictions)

            cluster = ContradictionCluster(
                theme=theme,
                contradictions=group_contradictions,
                affected_tribunals=sorted(tribunals),
                total_cases=len(group_contradictions) * 2,
                severity_distribution=dict(severity_dist),
                summary=summary
            )
            clusters.append(cluster)

        # Ordenar por número de contradições (maior primeiro)
        clusters.sort(key=lambda x: len(x.contradictions), reverse=True)

        return clusters

    def _generate_cluster_summary(
        self,
        theme: str,
        contradictions: List[Contradiction]
    ) -> str:
        """Gera resumo de um cluster de contradições"""
        tribunals = set()
        for c in contradictions:
            tribunals.add(c.case1.tribunal)
            tribunals.add(c.case2.tribunal)

        return (f"Tema '{theme}' apresenta {len(contradictions)} contradição(ões) "
                f"envolvendo {len(tribunals)} tribunal(is): {', '.join(sorted(tribunals))}")

    def _calculate_tribunal_statistics(
        self,
        cases: List[JurisprudenceCase],
        contradictions: List[Contradiction]
    ) -> Dict[str, Dict]:
        """Calcula estatísticas por tribunal"""
        stats = defaultdict(lambda: {
            'total_cases': 0,
            'contradictions_involved': 0,
            'contradiction_rate': 0.0,
            'severity_distribution': defaultdict(int)
        })

        # Contar casos por tribunal
        for case in cases:
            stats[case.tribunal]['total_cases'] += 1

        # Contar contradições por tribunal
        for contradiction in contradictions:
            for case in [contradiction.case1, contradiction.case2]:
                stats[case.tribunal]['contradictions_involved'] += 1
                stats[case.tribunal]['severity_distribution'][
                    contradiction.contradiction_severity
                ] += 1

        # Calcular taxas
        for tribunal, data in stats.items():
            if data['total_cases'] > 0:
                data['contradiction_rate'] = (
                    data['contradictions_involved'] / data['total_cases']
                )

        return dict(stats)

    def _generate_highlights(
        self,
        contradictions: List[Contradiction],
        clusters: List[ContradictionCluster]
    ) -> List[str]:
        """Gera principais descobertas"""
        highlights = []

        if not contradictions:
            highlights.append("✅ Nenhuma contradição crítica detectada")
            return highlights

        # Contradições críticas
        critical = [c for c in contradictions if c.contradiction_severity == "crítica"]
        if critical:
            highlights.append(
                f"🚨 {len(critical)} contradição(ões) CRÍTICA(S) detectada(s) "
                f"- requer atenção imediata"
            )

        # Cluster mais problemático
        if clusters:
            biggest_cluster = clusters[0]
            highlights.append(
                f"⚠️  Tema '{biggest_cluster.theme}' é o mais problemático "
                f"com {len(biggest_cluster.contradictions)} contradição(ões)"
            )

        # Tribunais mais divergentes
        tribunal_counts = defaultdict(int)
        for c in contradictions:
            tribunal_counts[c.case1.tribunal] += 1
            tribunal_counts[c.case2.tribunal] += 1

        if tribunal_counts:
            most_divergent = max(tribunal_counts.items(), key=lambda x: x[1])
            highlights.append(
                f"📊 {most_divergent[0]} aparece em {most_divergent[1]} contradição(ões)"
            )

        return highlights

    def _generate_recommendations(
        self,
        contradictions: List[Contradiction],
        clusters: List[ContradictionCluster]
    ) -> List[str]:
        """Gera recomendações estratégicas"""
        recommendations = []

        if not contradictions:
            recommendations.append(
                "Jurisprudência consistente - continue monitorando novas decisões"
            )
            return recommendations

        # Recomendações por gravidade
        critical = [c for c in contradictions if c.contradiction_severity == "crítica"]
        if critical:
            recommendations.append(
                "🚨 URGENTE: Analise contradições críticas antes de protocolizar petição"
            )

        # Recomendações por cluster
        if clusters and len(clusters[0].contradictions) >= 3:
            recommendations.append(
                f"💡 Considere arguir divergência jurisprudencial no tema "
                f"'{clusters[0].theme}'"
            )

        # Recomendação geral
        recommendations.append(
            "📚 Cite as decisões mais recentes e bem fundamentadas em sua petição"
        )

        recommendations.append(
            "⚖️  Monitore se há recurso especial ou extraordinário sobre o tema"
        )

        return recommendations

    def _create_empty_report(self, query: str, total_cases: int) -> ContradictionReport:
        """Cria relatório vazio quando não há dados suficientes"""
        return ContradictionReport(
            generated_at=datetime.now(),
            query=query,
            total_cases_analyzed=total_cases,
            contradictions_found=0,
            clusters=[],
            tribunal_comparison={},
            highlights=["ℹ️  Poucos casos encontrados para análise"],
            recommendations=["Tente uma consulta mais ampla ou adicione mais documentos à base"]
        )

    def create_alerts(
        self,
        contradictions: List[Contradiction],
        priority_threshold: str = "média"
    ) -> List[ContradictionAlert]:
        """
        Cria alertas a partir de contradições detectadas

        Args:
            contradictions: Lista de contradições
            priority_threshold: Prioridade mínima ("baixa", "média", "alta", "urgente")

        Returns:
            Lista de alertas
        """
        priority_map = {
            "baixa": {"baixa": "baixa"},
            "média": {"média": "média", "alta": "alta", "crítica": "urgente"},
            "alta": {"alta": "alta", "crítica": "urgente"},
            "crítica": {"crítica": "urgente"}
        }

        alerts = []

        for contradiction in contradictions:
            # Mapear gravidade para prioridade
            priority = "baixa"
            if contradiction.contradiction_severity in ["alta", "crítica"]:
                priority = "alta" if contradiction.contradiction_severity == "alta" else "urgente"
            elif contradiction.contradiction_severity == "média":
                priority = "média"

            # Criar mensagem
            message = f"""Contradição detectada entre {contradiction.case1.tribunal} e {contradiction.case2.tribunal}

{contradiction.explanation}

Impacto: {contradiction.legal_impact}"""

            alert = ContradictionAlert(
                contradiction=contradiction,
                priority=priority,
                message=message,
                actionable=contradiction.contradiction_severity in ["alta", "crítica"],
                tribunals_involved=[contradiction.case1.tribunal, contradiction.case2.tribunal]
            )

            alerts.append(alert)

        # Ordenar por prioridade (urgente primeiro)
        priority_order = {"urgente": 0, "alta": 1, "média": 2, "baixa": 3}
        alerts.sort(key=lambda x: priority_order[x.priority])

        return alerts

"""Gerador de embeddings usando a API da OpenAI.

Implementa geração de embeddings para textos, com suporte a
processamento em lote e retry automático em caso de falhas.
"""
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class EmbeddingGenerator:
    """Gerador de embeddings vetoriais usando modelos da OpenAI.

    Converte textos em vetores numéricos para busca semântica,
    com suporte a processamento individual e em lote.
    """

    def __init__(self, api_key: str | None = None) -> None:
        """Inicializa o gerador com credenciais da OpenAI.

        Args:
            api_key: Chave de API da OpenAI (usa settings se não fornecida).

        Raises:
            ValueError: Se a chave de API não estiver configurada.
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key não configurada")

        openai.api_key = self.api_key
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate_embedding(self, text: str) -> list[float]:
        """Gera embedding para um único texto.

        Args:
            text: Texto para gerar embedding.

        Returns:
            Vetor de embedding como lista de floats.

        Raises:
            openai.OpenAIError: Se a API retornar erro após todas as tentativas.
        """
        try:
            response = openai.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding
        except openai.OpenAIError as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            raise

    def generate_embeddings_batch(
        self,
        texts: list[str],
        batch_size: int = 100,
    ) -> list[list[float]]:
        """Gera embeddings em lote de forma eficiente.

        Args:
            texts: Lista de textos para processar.
            batch_size: Número de textos por requisição à API.

        Returns:
            Lista de embeddings na mesma ordem dos textos de entrada.
        """
        embeddings: list[list[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            logger.info(f"Gerando embeddings para lote {batch_num}")

            try:
                response = openai.embeddings.create(
                    model=self.model,
                    input=batch,
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            except openai.OpenAIError as e:
                logger.error(f"Erro no lote {batch_num}: {e}")
                # Fallback: processa individualmente com vetor zero para falhas
                for text in batch:
                    try:
                        emb = self.generate_embedding(text)
                        embeddings.append(emb)
                    except openai.OpenAIError:
                        logger.error("Falha ao gerar embedding individual")
                        embeddings.append([0.0] * self.dimension)

        return embeddings

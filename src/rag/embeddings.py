"""
Gerador de embeddings usando OpenAI
"""
from typing import List
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class EmbeddingGenerator:
    """Gerador de embeddings usando OpenAI"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key não configurada")

        openai.api_key = self.api_key
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um texto

        Args:
            text: Texto para gerar embedding

        Returns:
            Vetor de embedding
        """
        try:
            response = openai.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            raise

    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Gera embeddings em lote

        Args:
            texts: Lista de textos
            batch_size: Tamanho do lote

        Returns:
            Lista de embeddings
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Gerando embeddings para lote {i//batch_size + 1}")

            try:
                response = openai.embeddings.create(
                    model=self.model,
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Erro no lote {i//batch_size + 1}: {e}")
                # Fallback: processar individualmente
                for text in batch:
                    try:
                        emb = self.generate_embedding(text)
                        embeddings.append(emb)
                    except:
                        logger.error(f"Falha ao gerar embedding individual")
                        embeddings.append([0.0] * self.dimension)

        return embeddings

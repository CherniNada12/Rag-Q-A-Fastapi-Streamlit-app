from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging
from .config import config

logger = logging.getLogger(__name__)

class EmbeddingModel:
    """Gestion des embeddings avec Sentence Transformers"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.EMBEDDING_MODEL
        logger.info(f"Chargement du modèle : {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        logger.info("Modèle chargé avec succès")
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encode une liste de textes en embeddings
        
        Args:
            texts: Liste de textes
            
        Returns:
            Array numpy des embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        logger.info(f"Encoding de {len(texts)} textes...")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        logger.info("Encoding terminé")
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Retourne la dimension des embeddings"""
        return self.model.get_sentence_embedding_dimension()
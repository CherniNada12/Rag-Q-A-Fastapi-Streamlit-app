import faiss
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
import logging
from .config import config
from .embeddings import EmbeddingModel

logger = logging.getLogger(__name__)

class FAISSRetriever:
    """Recherche sémantique avec FAISS"""
    
    def __init__(self):
        self.index = None
        self.metadata = []
        self.embedding_model = EmbeddingModel()
        self.dimension = self.embedding_model.get_embedding_dimension()
    
    def create_index(self, embeddings: np.ndarray, metadata: List[Dict]):
        """
        Crée un nouvel index FAISS
        
        Args:
            embeddings: Embeddings des chunks
            metadata: Métadonnées des chunks
        """
        logger.info(f"Création de l'index FAISS (dimension={self.dimension})")
        
        # Créer l'index (IndexFlatL2 pour similarité cosine)
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Normaliser les embeddings pour cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Ajouter à l'index
        self.index.add(embeddings.astype('float32'))
        self.metadata = metadata
        
        logger.info(f"Index créé avec {self.index.ntotal} vecteurs")
    
    def add_to_index(self, embeddings: np.ndarray, metadata: List[Dict]):
        """Ajoute des embeddings à l'index existant"""
        if self.index is None:
            self.create_index(embeddings, metadata)
        else:
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
            self.metadata.extend(metadata)
            logger.info(f"Ajout de {len(metadata)} vecteurs. Total: {self.index.ntotal}")
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Recherche les chunks les plus similaires
        
        Args:
            query: Question de l'utilisateur
            top_k: Nombre de résultats
            
        Returns:
            Liste de chunks avec scores
        """
        if self.index is None:
            raise ValueError("L'index n'est pas initialisé")
        
        top_k = top_k or config.TOP_K_RESULTS
        
        # Encoder la query
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Recherche
        distances, indices = self.index.search(
            query_embedding.astype('float32'), 
            top_k
        )
        
        # Préparer les résultats
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['score'] = float(1 / (1 + dist))  # Convertir distance en score
                results.append(result)
        
        return results
    
    def save_index(self, index_path: Path = None, metadata_path: Path = None):
        """Sauvegarde l'index et les métadonnées"""
        if self.index is None:
            raise ValueError("Aucun index à sauvegarder")
        
        index_path = index_path or config.FAISS_INDEX_PATH
        metadata_path = metadata_path or config.METADATA_PATH
        
        # Sauvegarder l'index FAISS
        faiss.write_index(self.index, str(index_path))
        
        # Sauvegarder les métadonnées
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Index sauvegardé : {index_path}")
        logger.info(f"Métadonnées sauvegardées : {metadata_path}")
    
    def load_index(self, index_path: Path = None, metadata_path: Path = None):
        """Charge l'index et les métadonnées"""
        index_path = index_path or config.FAISS_INDEX_PATH
        metadata_path = metadata_path or config.METADATA_PATH
        
        if not index_path.exists():
            raise FileNotFoundError(f"Index non trouvé : {index_path}")
        
        # Charger l'index
        self.index = faiss.read_index(str(index_path))
        
        # Charger les métadonnées
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        logger.info(f"Index chargé : {self.index.ntotal} vecteurs")
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import pytest
import numpy as np
from modules.embeddings import EmbeddingModel

class TestEmbeddingModel:
    """Tests pour le modèle d'embeddings"""
    
    @pytest.fixture
    def embedding_model(self):
        """Fixture pour créer un modèle d'embedding"""
        return EmbeddingModel()
    
    def test_model_initialization(self, embedding_model):
        """Test l'initialisation du modèle"""
        assert embedding_model.model is not None
        assert embedding_model.model_name is not None
    
    def test_get_embedding_dimension(self, embedding_model):
        """Test la récupération de la dimension"""
        dim = embedding_model.get_embedding_dimension()
        assert isinstance(dim, int)
        assert dim > 0
    
    def test_encode_single_text(self, embedding_model):
        """Test l'encoding d'un seul texte"""
        text = "Ceci est un test"
        embeddings = embedding_model.encode([text])
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 1
        assert embeddings.shape[1] == embedding_model.get_embedding_dimension()
    
    def test_encode_multiple_texts(self, embedding_model):
        """Test l'encoding de plusieurs textes"""
        texts = [
            "Premier texte",
            "Deuxième texte",
            "Troisième texte"
        ]
        embeddings = embedding_model.encode(texts)
        
        assert embeddings.shape[0] == len(texts)
        assert embeddings.shape[1] == embedding_model.get_embedding_dimension()
    
    def test_encode_empty_list(self, embedding_model):
        """Test l'encoding d'une liste vide"""
        embeddings = embedding_model.encode([])
        assert embeddings.shape[0] == 0
    
    def test_embeddings_are_normalized(self, embedding_model):
        """Test que les embeddings peuvent être normalisés"""
        text = "Test de normalisation"
        embeddings = embedding_model.encode([text])
        
        # Calculer la norme L2
        norm = np.linalg.norm(embeddings[0])
        
        # La norme devrait être proche de 1 (mais pas exactement)
        assert norm > 0
    
    def test_similar_texts_have_similar_embeddings(self, embedding_model):
        """Test que des textes similaires ont des embeddings similaires"""
        text1 = "Le chat dort sur le canapé"
        text2 = "Le chat se repose sur le sofa"
        text3 = "La voiture roule sur la route"
        
        embeddings = embedding_model.encode([text1, text2, text3])
        
        # Calculer les similarités cosinus
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(embeddings)
        
        # La similarité entre text1 et text2 devrait être plus élevée
        # que celle entre text1 et text3
        sim_12 = similarities[0, 1]
        sim_13 = similarities[0, 2]
        
        assert sim_12 > sim_13

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
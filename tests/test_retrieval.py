import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import pytest
import numpy as np
from modules.retrieval import FAISSRetriever

class TestFAISSRetriever:
    """Tests pour le système de retrieval FAISS"""
    
    @pytest.fixture
    def sample_data(self):
        """Fixture avec des données d'exemple"""
        texts = [
            "Le machine learning est une branche de l'IA",
            "Le deep learning utilise des réseaux de neurones",
            "Python est un langage de programmation",
            "La data science analyse les données",
            "L'intelligence artificielle simule l'intelligence humaine"
        ]
        
        metadata = [
            {
                'chunk_id': f'chunk_{i}',
                'content': text,
                'document_name': 'test.txt',
                'chunk_index': i
            }
            for i, text in enumerate(texts)
        ]
        
        return texts, metadata
    
    @pytest.fixture
    def retriever_with_data(self, sample_data):
        """Fixture avec un retriever initialisé"""
        texts, metadata = sample_data
        
        retriever = FAISSRetriever()
        embeddings = retriever.embedding_model.encode(texts)
        retriever.create_index(embeddings, metadata)
        
        return retriever
    
    def test_retriever_initialization(self):
        """Test l'initialisation du retriever"""
        retriever = FAISSRetriever()
        assert retriever.index is None
        assert retriever.metadata == []
        assert retriever.embedding_model is not None
    
    def test_create_index(self, sample_data):
        """Test la création d'un index"""
        texts, metadata = sample_data
        
        retriever = FAISSRetriever()
        embeddings = retriever.embedding_model.encode(texts)
        retriever.create_index(embeddings, metadata)
        
        assert retriever.index is not None
        assert retriever.index.ntotal == len(texts)
        assert len(retriever.metadata) == len(texts)
    
    def test_search_returns_results(self, retriever_with_data):
        """Test que la recherche retourne des résultats"""
        query = "Qu'est-ce que le machine learning ?"
        results = retriever_with_data.search(query, top_k=3)
        
        assert len(results) == 3
        assert all('score' in r for r in results)
        assert all('content' in r for r in results)
    
    def test_search_relevance(self, retriever_with_data):
        """Test la pertinence des résultats"""
        query = "réseaux de neurones"
        results = retriever_with_data.search(query, top_k=1)
        
        # Le premier résultat devrait contenir "réseaux de neurones"
        assert "neurones" in results[0]['content'].lower()
    
    def test_search_scores_are_descending(self, retriever_with_data):
        """Test que les scores sont triés par ordre décroissant"""
        query = "intelligence artificielle"
        results = retriever_with_data.search(query, top_k=5)
        
        scores = [r['score'] for r in results]
        assert scores == sorted(scores, reverse=True)
    
    def test_search_without_index_raises_error(self):
        """Test qu'une recherche sans index lève une erreur"""
        retriever = FAISSRetriever()
        
        with pytest.raises(ValueError):
            retriever.search("test query")
    
    def test_add_to_index(self, retriever_with_data, sample_data):
        """Test l'ajout de nouveaux vecteurs à l'index"""
        initial_count = retriever_with_data.index.ntotal
        
        new_text = "Nouveau texte à ajouter"
        new_metadata = [{
            'chunk_id': 'new_chunk',
            'content': new_text,
            'document_name': 'new.txt',
            'chunk_index': 0
        }]
        
        new_embedding = retriever_with_data.embedding_model.encode([new_text])
        retriever_with_data.add_to_index(new_embedding, new_metadata)
        
        assert retriever_with_data.index.ntotal == initial_count + 1
    
    def test_save_and_load_index(self, retriever_with_data, tmp_path):
        """Test la sauvegarde et le chargement de l'index"""
        # Sauvegarder
        index_path = tmp_path / "test_index.bin"
        metadata_path = tmp_path / "test_metadata.json"
        
        retriever_with_data.save_index(index_path, metadata_path)
        
        assert index_path.exists()
        assert metadata_path.exists()
        
        # Charger dans un nouveau retriever
        new_retriever = FAISSRetriever()
        new_retriever.load_index(index_path, metadata_path)
        
        assert new_retriever.index.ntotal == retriever_with_data.index.ntotal
        assert len(new_retriever.metadata) == len(retriever_with_data.metadata)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
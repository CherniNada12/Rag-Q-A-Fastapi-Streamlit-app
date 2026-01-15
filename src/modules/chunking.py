from typing import List, Dict
import re
from .config import config

class TextChunker:
    """Découpage de texte en chunks"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP
    
    def clean_text(self, text: str) -> str:
        """Nettoie le texte"""
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        # Supprimer les sauts de ligne multiples
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        Découpe le texte en chunks avec overlap
        
        Args:
            text: Texte à découper
            
        Returns:
            Liste de chunks
        """
        text = self.clean_text(text)
        words = text.split()
        chunks = []
        
        i = 0
        while i < len(words):
            # Prendre chunk_size mots
            chunk_words = words[i:i + self.chunk_size]
            chunk = ' '.join(chunk_words)
            chunks.append(chunk)
            
            # Avancer de (chunk_size - overlap) pour créer l'overlap
            i += (self.chunk_size - self.chunk_overlap)
        
        return chunks
    
    def create_chunks_with_metadata(
        self, 
        text: str, 
        document_name: str
    ) -> List[Dict[str, any]]:
        """
        Crée des chunks avec métadonnées
        
        Args:
            text: Texte source
            document_name: Nom du document
            
        Returns:
            Liste de dicts avec chunk et métadonnées
        """
        chunks = self.split_into_chunks(text)
        
        chunks_with_metadata = []
        for idx, chunk in enumerate(chunks):
            chunks_with_metadata.append({
                'chunk_id': f"{document_name}_{idx}",
                'document_name': document_name,
                'chunk_index': idx,
                'content': chunk,
                'num_words': len(chunk.split()),
                'num_characters': len(chunk)
            })
        
        return chunks_with_metadata
import PyPDF2
import docx
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class DocumentIngestion:
    """Gestion de l'ingestion des documents"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: Path) -> str:
        """Extrait le texte d'un fichier PDF"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction PDF : {e}")
            raise
    
    @staticmethod
    def extract_text_from_docx(file_path: Path) -> str:
        """Extrait le texte d'un fichier DOCX"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction DOCX : {e}")
            raise
    
    @staticmethod
    def extract_text_from_txt(file_path: Path) -> str:
        """Extrait le texte d'un fichier TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction TXT : {e}")
            raise
    
    def process_document(self, file_path: Path) -> Dict[str, str]:
        """
        Traite un document et retourne son contenu
        
        Args:
            file_path: Chemin vers le document
            
        Returns:
            Dict avec 'filename', 'extension', 'content'
        """
        extension = file_path.suffix.lower()
        
        extractors = {
            '.pdf': self.extract_text_from_pdf,
            '.docx': self.extract_text_from_docx,
            '.txt': self.extract_text_from_txt
        }
        
        if extension not in extractors:
            raise ValueError(
                f"Format non supporté : {extension}. "
                f"Formats acceptés : {list(extractors.keys())}"
            )
        
        content = extractors[extension](file_path)
        
        return {
            'filename': file_path.name,
            'extension': extension,
            'content': content,
            'num_characters': len(content)
        }
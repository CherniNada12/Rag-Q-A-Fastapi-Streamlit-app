import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    """Configuration centralisée du projet"""
    
    # Chemins
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    DOCUMENTS_DIR = DATA_DIR / "documents"
    CHUNKS_DIR = DATA_DIR / "chunks"
    INDEX_DIR = DATA_DIR / "index"
    
    # Créer les répertoires s'ils n'existent pas
    for directory in [DOCUMENTS_DIR, CHUNKS_DIR, INDEX_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Configuration RAG
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 5))
    
    # Modèles
    EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    r"C:\Users\nadac\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2"
    )

    LLM_MODEL = os.getenv("LLM_MODEL", "gpt2")
    
    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # OpenAI (optionnel)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Index FAISS
    FAISS_INDEX_PATH = INDEX_DIR / "faiss_index.bin"
    METADATA_PATH = INDEX_DIR / "metadata.json"

config = Config()
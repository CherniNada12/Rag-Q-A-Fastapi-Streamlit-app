from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import shutil
from pathlib import Path
import logging
import sys

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from modules.config import config
from modules.ingestion import DocumentIngestion
from modules.chunking import TextChunker
from modules.embeddings import EmbeddingModel
from modules.retrieval import FAISSRetriever
from modules.generation import ResponseGenerator

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialiser FastAPI
app = FastAPI(
    title="RAG API",
    description="API pour système RAG avec FAISS et LLM",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser les composants
retriever = FAISSRetriever()
generator = ResponseGenerator()
ingestion = DocumentIngestion()
chunker = TextChunker()

# Charger l'index existant si disponible
try:
    retriever.load_index()
    logger.info("Index FAISS chargé avec succès")
except FileNotFoundError:
    logger.info("Aucun index existant, un nouveau sera créé")

# Modèles Pydantic
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict]
    context_used: int
    retrieved_chunks: List[Dict]

class DocumentInfo(BaseModel):
    filename: str
    num_chunks: int
    num_characters: int

# Routes
@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Bienvenue sur l'API RAG",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload_document",
            "query": "/query",
            "documents": "/list_documents",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Vérification de santé du serveur"""
    index_status = "loaded" if retriever.index is not None else "not_loaded"
    num_vectors = retriever.index.ntotal if retriever.index else 0
    
    return {
        "status": "healthy",
        "index_status": index_status,
        "num_vectors": num_vectors,
        "embedding_model": config.EMBEDDING_MODEL,
        "llm_model": config.LLM_MODEL
    }

@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload et traitement d'un document
    
    - Extrait le texte
    - Crée des chunks
    - Génère les embeddings
    - Ajoute à l'index FAISS
    """
    try:
        # Sauvegarder le fichier
        file_path = config.DOCUMENTS_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Fichier reçu : {file.filename}")
        
        # 1. Extraction du texte
        doc_info = ingestion.process_document(file_path)
        logger.info(f"Texte extrait : {doc_info['num_characters']} caractères")
        
        # 2. Chunking
        chunks_with_metadata = chunker.create_chunks_with_metadata(
            doc_info['content'],
            doc_info['filename']
        )
        logger.info(f"Chunks créés : {len(chunks_with_metadata)}")
        
        # 3. Embeddings
        chunk_texts = [chunk['content'] for chunk in chunks_with_metadata]
        embeddings = retriever.embedding_model.encode(chunk_texts)
        logger.info(f"Embeddings générés : {embeddings.shape}")
        
        # 4. Ajout à l'index
        retriever.add_to_index(embeddings, chunks_with_metadata)
        
        # 5. Sauvegarder l'index
        retriever.save_index()
        
        return {
            "status": "success",
            "filename": file.filename,
            "num_chunks": len(chunks_with_metadata),
            "num_characters": doc_info['num_characters'],
            "total_vectors_in_index": retriever.index.ntotal
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'upload : {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Effectue une requête RAG
    
    - Recherche les chunks pertinents
    - Génère une réponse avec le LLM
    """
    try:
        if retriever.index is None:
            raise HTTPException(
                status_code=400,
                detail="Aucun document indexé. Veuillez d'abord uploader des documents."
            )
        
        logger.info(f"Question reçue : {request.question}")
        
        # 1. Recherche des chunks pertinents
        retrieved_chunks = retriever.search(
            request.question,
            top_k=request.top_k
        )
        logger.info(f"Chunks récupérés : {len(retrieved_chunks)}")
        
        # 2. Génération de la réponse
        response = generator.generate_answer(
            request.question,
            retrieved_chunks
        )
        logger.info("Réponse générée")
        
        return QueryResponse(
            answer=response['answer'],
            sources=response['sources'],
            context_used=response['context_used'],
            retrieved_chunks=retrieved_chunks
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la requête : {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_documents")
async def list_documents():
    """Liste tous les documents indexés"""
    try:
        if not retriever.metadata:
            return {"documents": [], "total": 0}
        
        # Extraire les noms de documents uniques
        document_names = list(set(
            chunk['document_name'] for chunk in retriever.metadata
        ))
        
        # Compter les chunks par document
        documents_info = []
        for doc_name in document_names:
            chunks = [
                chunk for chunk in retriever.metadata 
                if chunk['document_name'] == doc_name
            ]
            documents_info.append({
                "filename": doc_name,
                "num_chunks": len(chunks),
                "total_characters": sum(chunk['num_characters'] for chunk in chunks)
            })
        
        return {
            "documents": documents_info,
            "total": len(documents_info),
            "total_chunks": len(retriever.metadata)
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du listing : {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear_index")
async def clear_index():
    """Supprime tous les documents de l'index"""
    try:
        retriever.index = None
        retriever.metadata = []
        
        # Supprimer les fichiers d'index
        if config.FAISS_INDEX_PATH.exists():
            config.FAISS_INDEX_PATH.unlink()
        if config.METADATA_PATH.exists():
            config.METADATA_PATH.unlink()
        
        logger.info("Index supprimé")
        return {"status": "success", "message": "Index cleared"}
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression : {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Lancement du serveur
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
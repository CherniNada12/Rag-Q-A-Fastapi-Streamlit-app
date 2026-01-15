from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import shutil
import logging
import sys

# Ajouter le chemin des modules
sys.path.append(str(Path(__file__).parent.parent))

from modules.ingestion import DocumentIngestion
from modules.chunking import TextChunker
from modules.retrieval import FAISSRetriever
from modules.generation import ResponseGenerator
from modules.config import config

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialisation FastAPI
app = FastAPI(
    title="RAG System API",
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

# Initialisation des composants
ingestion = DocumentIngestion()
chunker = TextChunker()
retriever = FAISSRetriever()
generator = ResponseGenerator()

# =========================
# Modèles Pydantic
# =========================

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    retrieved_chunks: list
    sources: list
    context_used: int

# =========================
# Endpoints
# =========================

@app.get("/")
def read_root():
    """Page d'accueil"""
    return {
        "message": "API RAG opérationnelle",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    """Vérification de l'état du système"""
    num_vectors = retriever.index.ntotal if retriever.index else 0
    
    return {
        "status": "healthy",
        "num_vectors": num_vectors,
        "embedding_model": retriever.embedding_model.model_name,
        "llm_model": generator.model_name
    }

@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload et indexation d'un document
    
    Args:
        file: Fichier PDF, DOCX ou TXT
        
    Returns:
        Informations sur le document indexé
    """
    try:
        # Vérifier l'extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.pdf', '.txt', '.docx']:
            raise HTTPException(
                status_code=400,
                detail=f"Format non supporté: {file_ext}"
            )
        
        # Sauvegarder temporairement
        temp_path = config.DOCUMENTS_DIR / file.filename
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"📄 Document reçu: {file.filename}")
        
        # 1. Ingestion
        doc_info = ingestion.process_document(temp_path)
        
        # 2. Chunking
        chunks = chunker.create_chunks_with_metadata(
            doc_info['content'],
            doc_info['filename']
        )
        
        # 3. Embeddings
        chunk_texts = [c['content'] for c in chunks]
        embeddings = retriever.embedding_model.encode(chunk_texts)
        
        # 4. Indexation
        retriever.add_to_index(embeddings, chunks)
        
        # 5. Sauvegarder l'index
        retriever.save_index()
        
        logger.info(f"✅ Document indexé: {file.filename}")
        
        return {
            "filename": doc_info['filename'],
            "num_chunks": len(chunks),
            "num_characters": doc_info['num_characters'],
            "total_vectors": retriever.index.ntotal
        }
        
    except Exception as e:
        logger.error(f"Erreur upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_documents")
def list_documents():
    """Liste les documents indexés"""
    if not retriever.metadata:
        return {"documents": [], "total": 0}
    
    # Grouper par document
    docs_info = {}
    for meta in retriever.metadata:
        doc_name = meta['document_name']
        if doc_name not in docs_info:
            docs_info[doc_name] = {
                'filename': doc_name,
                'num_chunks': 0,
                'total_characters': 0
            }
        docs_info[doc_name]['num_chunks'] += 1
        docs_info[doc_name]['total_characters'] += meta.get('num_characters', 0)
    
    return {
        "documents": list(docs_info.values()),
        "total": len(docs_info)
    }

@app.post("/query", response_model=QueryResponse)
def query_system(request: QueryRequest):
    """
    Pose une question au système RAG
    
    Args:
        request: Question et paramètres
        
    Returns:
        Réponse générée avec sources
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question vide")
        
        logger.info(f"🔍 Question reçue: {request.question[:50]}...")
        
        # 1. Recherche
        retrieved_chunks = retriever.search(request.question, top_k=request.top_k)
        
        if not retrieved_chunks:
            return QueryResponse(
                answer="Je n'ai pas trouvé d'information pertinente dans les documents.",
                retrieved_chunks=[],
                sources=[],
                context_used=0
            )
        
        # 2. Génération
        result = generator.generate_answer(request.question, retrieved_chunks)
        
        logger.info(f"✅ Réponse générée avec {result['context_used']} chunks")
        
        return QueryResponse(
            answer=result['answer'],
            retrieved_chunks=retrieved_chunks,
            sources=result['sources'],
            context_used=result['context_used']
        )
        
    except Exception as e:
        logger.error(f"Erreur query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear_index")
def clear_index():
    """Vide complètement l'index"""
    try:
        retriever.clear_index()
        retriever.save_index()
        return {"message": "Index vidé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
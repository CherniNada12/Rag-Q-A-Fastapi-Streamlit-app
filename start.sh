#!/bin/bash

# Script de démarrage du système RAG

echo "🚀 Démarrage du système RAG..."
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 détecté${NC}"

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Création de l'environnement virtuel...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
fi

# Activer l'environnement virtuel
echo -e "${BLUE}🔧 Activation de l'environnement virtuel...${NC}"
source venv/bin/activate

# Installer les dépendances si nécessaire
if [ ! -f "venv/installed" ]; then
    echo -e "${BLUE}📥 Installation des dépendances...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/installed
    echo -e "${GREEN}✅ Dépendances installées${NC}"
fi

# Créer les répertoires nécessaires
mkdir -p data/documents data/chunks data/index

# Vérifier si le fichier .env existe
if [ ! -f ".env" ]; then
    echo -e "${RED}⚠️  Fichier .env manquant${NC}"
    echo -e "${BLUE}📝 Création du fichier .env...${NC}"
    cp .env.example .env 2>/dev/null || cat > .env << EOF
PROJECT_NAME="RAG FastAPI Streamlit"
ENVIRONMENT="development"
DATA_DIR="./data"
DOCUMENTS_DIR="./data/documents"
CHUNKS_DIR="./data/chunks"
INDEX_DIR="./data/index"
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL="gpt2"
OPENAI_API_KEY=""
API_HOST="0.0.0.0"
API_PORT=8000
STREAMLIT_PORT=8501
EOF
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Système RAG prêt à démarrer!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Menu de choix
echo "Que voulez-vous démarrer ?"
echo ""
echo "1) API FastAPI uniquement"
echo "2) Interface Streamlit uniquement"
echo "3) Les deux (API + Streamlit)"
echo "4) Tests avec Jupyter Notebook"
echo "5) Quitter"
echo ""
read -p "Votre choix (1-5): " choice

case $choice in
    1)
        echo -e "${BLUE}🚀 Démarrage de l'API FastAPI...${NC}"
        cd src/api
        python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
        ;;
    2)
        echo -e "${BLUE}🚀 Démarrage de Streamlit...${NC}"
        cd src/frontend
        streamlit run app.py
        ;;
    3)
        echo -e "${BLUE}🚀 Démarrage de l'API et Streamlit...${NC}"
        echo -e "${BLUE}📡 API sur http://localhost:8000${NC}"
        echo -e "${BLUE}🌐 Streamlit sur http://localhost:8501${NC}"
        
        # Démarrer l'API en arrière-plan
        cd src/api
        python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
        API_PID=$!
        cd ../..
        
        # Attendre que l'API démarre
        sleep 3
        
        # Démarrer Streamlit
        cd src/frontend
        streamlit run app.py
        
        # Tuer l'API à la fin
        kill $API_PID
        ;;
    4)
        echo -e "${BLUE}📓 Démarrage de Jupyter Notebook...${NC}"
        jupyter notebook notebooks/
        ;;
    5)
        echo -e "${GREEN}👋 Au revoir!${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Choix invalide${NC}"
        exit 1
        ;;
esac
#!/bin/bash

# Script de démarrage du Learning Assistant RAG

echo "🚀 Démarrage du Learning Assistant RAG..."
echo "==========================================="

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Environnement virtuel non trouvé${NC}"
    echo "Création de l'environnement virtuel..."
    python -m venv venv
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
fi

# Activer l'environnement virtuel
echo "Activation de l'environnement virtuel..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo -e "${GREEN}✅ Environnement activé${NC}"

# Installer les dépendances si nécessaire
if [ ! -f "venv/.dependencies_installed" ]; then
    echo "Installation des dépendances..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.dependencies_installed
    echo -e "${GREEN}✅ Dépendances installées${NC}"
fi

# Créer les dossiers nécessaires
echo "Vérification de la structure des dossiers..."
mkdir -p data/documents data/chunks data/index
echo -e "${GREEN}✅ Dossiers vérifiés${NC}"

# Vérifier le fichier .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Fichier .env non trouvé${NC}"
    echo "Création du fichier .env par défaut..."
    cat > .env << EOF
# Configuration Learning Assistant RAG
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL="gpt2"
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
API_HOST="0.0.0.0"
API_PORT=8000
OPENAI_API_KEY=""
EOF
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
fi

echo ""
echo "==========================================="
echo -e "${BLUE}🎓 Learning Assistant RAG est prêt !${NC}"
echo "==========================================="
echo ""

# Proposer le mode de démarrage
echo "Choisissez le mode de démarrage :"
echo "1) API seulement (FastAPI)"
echo "2) Interface seulement (Streamlit)"
echo "3) Les deux (recommandé)"
echo ""
read -p "Votre choix (1/2/3): " choice

case $choice in
    1)
        echo -e "${BLUE}🚀 Démarrage de l'API FastAPI...${NC}"
        cd src/api
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
        ;;
    2)
        echo -e "${BLUE}🚀 Démarrage de Streamlit...${NC}"
        cd src/frontend
        streamlit run learning_app.py
        ;;
    3)
        echo -e "${BLUE}🚀 Démarrage de l'API et de Streamlit...${NC}"
        
        # Démarrer l'API en arrière-plan
        cd src/api
        uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
        API_PID=$!
        
        # Attendre que l'API démarre
        echo "Attente du démarrage de l'API..."
        sleep 5
        
        # Démarrer Streamlit
        cd ../frontend
        streamlit run learning_app.py
        
        # Quand Streamlit se ferme, tuer l'API
        kill $API_PID
        ;;
    *)
        echo -e "${YELLOW}Choix invalide${NC}"
        exit 1
        ;;
esac
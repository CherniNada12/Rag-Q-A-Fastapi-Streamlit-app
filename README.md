**##🎓 RAG – Learning Assistant Spécialisé**

🧠 Domaine : Éducation / Formation numérique

FastAPI + Streamlit

Assistant pédagogique intelligent basé sur des documents éducatifs utilisant Retrieval-Augmented Generation (RAG), exposé via FastAPI et accessible par une interface Streamlit.
## 🎯 Objectif pédagogique

Ce projet vise à développer un Learning Assistant spécialisé, capable d’accompagner les apprenants en répondant à leurs questions uniquement à partir de supports pédagogiques fournis (cours, polycopiés, FAQ, documents PDF/TXT).

## 📋 Table des matières

- [Caractéristiques](#caractéristiques)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [API Documentation](#api-documentation)
- [Déploiement](#déploiement)
- [Tests](#tests)

## Structure du projet

RAG-FASTAPI-STREAMLIT/
├── data/ # Données brutes et préparées
├── notebooks/ # Notebooks pour exploration et test
│ ├── 01_Data_Ingestion_and_Chunking.ipynb
│ ├── 02_Embedding_and_FAISS_Index.ipynb
│ ├── 03_Test_RAG_Pipeline.ipynb
│ └── Demo_Learning_Assistant.ipynb
├── src/
│ ├── api/
│ │ └── main.py # FastAPI backend
│ ├── frontend/
│ │ └── learning_app.py # Streamlit frontend
│ └── modules/ # Modules de traitement et RAG
│ ├── learning_config.py
│ ├── chunking.py
│ ├── embeddings.py
│ ├── ingestion.py
│ ├── retrieval.py
│ └── learning_generator.py
├── tests/ # Tests unitaires
├── requirements.txt # Dépendances Python
├── .env # Variables d'environnement
├── start.sh # Script Linux/Mac pour lancer
├── start.bat # Script Windows pour lancer
├── README.md
├── INTEGRATION_GUIDE.md
└── MIGRATION_GUIDE.md

## ✨ Caractéristiques

- 📤 **Upload de documents** (PDF, DOCX, TXT)
- 🔪 **Chunking intelligent** avec overlap configurable
- 🧠 **Embeddings** avec Sentence Transformers
- 🔍 **Recherche sémantique** via FAISS
- 🤖 **Génération de réponses** avec LLM
- 🌐 **API REST** avec FastAPI
- 🎨 **Interface utilisateur** avec Streamlit
- 💾 **Persistance** de l'index FAISS
- 🐳 **Dockerisé** pour déploiement facile

## 🏗 Architecture

```
┌────────────────────┐
│  Documents éducatifs│
│ (Cours / Polycopiés)│
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Ingestion &        │
│  Chunking pédagogique│
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Embeddings         │
│ (SentenceTransformers)
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Index FAISS        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐      ┌────────────────────┐
│  Retrieval          │────▶ │  Génération        │
│  (passages cours)   │      │  pédagogique (LLM) │
└────────────────────┘      └─────────┬──────────┘
                                      │
                                      ▼
                           ┌────────────────────┐
                           │  Réponse explicative│
                           │  + sources          │
                           └────────────────────┘

```

## 🚀 Installation

### Prérequis

- Python 3.9+
- pip
- (Optionnel) Docker et Docker Compose

### Installation locale

1. **Cloner le repository**

```bash
git clone https://github.com/CherniNada12/Rag-Q-A-Fastapi-Streamlit-app.git
or
git clone https://github.com/MaysenChiha/Rag-Q-A-Fastapi-Streamlit-app.git

cd rag-fastapi-streamlit
```

2. **Créer l'environnement virtuel**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**

Copier `.env.example` vers `.env` et ajuster les valeurs :

```bash
cp .env.example .env
```

5. **Créer la structure des répertoires**

```bash
mkdir -p data/{documents,chunks,index}
```

## 📖 Utilisation

### Mode développement (local)

#### 1. Lancer l'API FastAPI

```bash
cd src/api
uvicorn main:app --reload --port 8000
```

L'API sera accessible sur : http://localhost:8000

Documentation interactive : http://localhost:8000/docs

#### 2. Lancer l'interface Streamlit

Dans un nouveau terminal :

```bash
cd src/frontend
streamlit run app.py
```

L'interface sera accessible sur : http://localhost:8501

### Mode Docker

#### 1. Construire et lancer avec Docker Compose

```bash
docker-compose up --build
```

Services disponibles :
- API : http://localhost:8000
- Frontend : http://localhost:8501

#### 2. Arrêter les services

```bash
docker-compose down
```

## 🔌 API Documentation

### Endpoints principaux

#### 1. Health Check

```bash
GET /health
```

Retourne le statut de l'API et des informations sur l'index.

#### 2. Upload de document

```bash
POST /upload_document
Content-Type: multipart/form-data

{
  "file": <fichier>
}
```

#### 3. Query (Question)

```bash
POST /query
Content-Type: application/json

{
  "question": "Votre question ici",
  "top_k": 5
}
```

**Réponse :**

```json
{
  "answer": "La réponse générée...",
  "sources": [...],
  "context_used": 3,
  "retrieved_chunks": [...]
}
```

#### 4. Liste des documents

```bash
GET /list_documents
```

#### 5. Supprimer l'index

```bash
DELETE /clear_index
```



## 📓 Notebooks

Trois notebooks Jupyter sont fournis pour explorer le pipeline :

1. **01_Data_Ingestion_and_Chunking.ipynb**
   - Extraction de texte
   - Découpage en chunks
   - Analyse des documents

2. **02_Embedding_and_FAISS_Index.ipynb**
   - Génération d'embeddings
   - Création de l'index FAISS
   - Tests de similarité

3. **03_Test_RAG_Pipeline.ipynb**
   - Pipeline complet
   - Tests de questions-réponses
   - Évaluation des performances

### Lancer les notebooks

```bash
jupyter notebook notebooks/
```

## 🧪 Tests

### Lancer les tests unitaires

```bash
pytest tests/ -v
```

### Tests spécifiques

```bash
# Tests d'embeddings
pytest tests/test_embeddings.py

# Tests de retrieval
pytest tests/test_retrieval.py

# Tests de génération
pytest tests/test_generation.py

# Tests API
pytest tests/test_api.py
```

## ⚙️ Configuration

### Fichier `.env`

```env
# Chemins
DATA_DIR=./data
DOCUMENTS_DIR=./data/documents
CHUNKS_DIR=./data/chunks
INDEX_DIR=./data/index

# RAG
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5

# Modèles
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=gpt2

# API
API_HOST=0.0.0.0
API_PORT=8000

# OpenAI (optionnel)
OPENAI_API_KEY=your-key-here
```

## 🐳 Déploiement

### Déploiement sur serveur VPS

1. **Cloner le projet sur le serveur**

```bash
git clone https://github.com/votre-username/rag-fastapi-streamlit.git
cd rag-fastapi-streamlit
```

2. **Configurer les variables d'environnement**

```bash
nano .env
```

3. **Lancer avec Docker Compose**

```bash
docker-compose up -d
```

4. **Vérifier les logs**

```bash
docker-compose logs -f
```

### Déploiement avec Nginx (reverse proxy)

Configuration Nginx pour l'API et Streamlit :

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    # API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Streamlit
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 📊 Monitoring

### Logs

```bash
# Logs de l'API
docker-compose logs api

# Logs du frontend
docker-compose logs frontend

# Tous les logs
docker-compose logs -f
```

### Métriques

Accéder aux métriques via :
- http://localhost:8000/metrics (si configuré)





## 👥 Auteurs

 - Nada Cherni & Maysen Chiha 

## 🙏 Remerciements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Hugging Face](https://huggingface.co/)



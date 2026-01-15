# 🔧 Guide d'Intégration - Learning Assistant RAG

Ce guide explique comment intégrer et personnaliser le Learning Assistant RAG dans votre environnement.

## 📋 Table des matières
1. [Installation rapide](#installation-rapide)
2. [Configuration](#configuration)
3. [Intégration dans l'API existante](#intégration-api)
4. [Personnalisation des prompts](#personnalisation-prompts)
5. [Ajout de nouveaux types de questions](#nouveaux-types)
6. [Utilisation programmatique](#utilisation-programmatique)
7. [Déploiement](#déploiement)

---

## 🚀 Installation rapide

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

### Windows
```batch
start.bat
```

---

## ⚙️ Configuration

### 1. Fichier `.env`

Créez un fichier `.env` à la racine :

```properties
# === Modèles ===
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL="gpt2"  # ou "openai" pour GPT

# === Configuration RAG ===
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5

# === API OpenAI (optionnel) ===
OPENAI_API_KEY="sk-..."

# === Serveurs ===
API_HOST="0.0.0.0"
API_PORT=8000
```

### 2. Modèles supportés

#### Embeddings
- `sentence-transformers/all-MiniLM-L6-v2` (léger, rapide)
- `sentence-transformers/all-mpnet-base-v2` (meilleur qualité)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingue)

#### LLM
- `gpt2` (local, gratuit)
- `gpt2-medium` (meilleur)
- `openai` avec `OPENAI_API_KEY` (meilleur qualité)

---

## 🔌 Intégration dans l'API existante

### Méthode 1: Remplacer le générateur standard

Dans `src/api/main.py`, remplacez :

```python
from modules.generation import ResponseGenerator

generator = ResponseGenerator()
```

Par :

```python
from modules.learning_generator import LearningResponseGenerator

generator = LearningResponseGenerator(use_openai=False)  # ou True
```

### Méthode 2: Ajouter un endpoint spécial

Ajoutez un endpoint dédié au Learning Assistant :

```python
from modules.learning_generator import LearningResponseGenerator

learning_generator = LearningResponseGenerator()

@app.post("/query/learning")
def query_learning(request: QueryRequest, level: str = 'intermediate'):
    """Endpoint pédagogique avec adaptation au niveau"""
    
    # Recherche
    chunks = retriever.search(request.question, top_k=request.top_k)
    
    # Génération pédagogique
    result = learning_generator.generate_pedagogical_answer(
        question=request.question,
        context_chunks=chunks,
        learning_level=level
    )
    
    return {
        'answer': result['answer'],
        'sources': result['sources'],
        'question_type': result['question_type'],
        'level': result['learning_level'],
        'suggestions': result['follow_up_suggestions']
    }
```

---

## 📝 Personnalisation des prompts

### 1. Modifier les prompts de niveau

Éditez `src/modules/learning_config.py` :

```python
LEARNING_PROMPTS = {
    'beginner': """
    Tu es un tuteur bienveillant pour débutants.
    
    Règles :
    - Vocabulaire simple
    - Analogies concrètes
    - Exemples du quotidien
    - Encouragements
    
    Contexte: {context}
    Question: {question}
    
    Réponds simplement :
    """,
    
    'intermediate': """
    Tu es un professeur expérimenté.
    
    Règles :
    - Explications structurées
    - Liens entre concepts
    - Exemples variés
    - Pistes de réflexion
    
    Contexte: {context}
    Question: {question}
    
    Réponds de manière claire :
    """,
    
    'advanced': """
    Tu es un expert académique.
    
    Règles :
    - Rigueur technique
    - Citations précises
    - Approfondissements
    - Nuances et subtilités
    
    Contexte: {context}
    Question: {question}
    
    Réponds avec précision :
    """
}
```

### 2. Personnaliser les formats de réponse

Modifiez `RESPONSE_FORMATS` :

```python
RESPONSE_FORMATS = {
    'definition': {
        'intro': 'Voici une définition claire :',
        'structure': [
            '1. Définition de base',
            '2. Caractéristiques principales',
            '3. Importance dans le domaine'
        ]
    },
    'your_custom_type': {
        'intro': 'Votre introduction personnalisée',
        'structure': ['Point 1', 'Point 2', 'Point 3']
    }
}
```

---

## ➕ Ajout de nouveaux types de questions

### 1. Définir les mots-clés

Dans `learning_config.py` :

```python
QUESTION_TYPES = {
    # Types existants...
    'definition': ['c\'est quoi', 'définir'],
    'explanation': ['comment', 'pourquoi'],
    
    # Nouveau type
    'exercise': ['exercice', 'pratique', 'entraînement', 's\'exercer'],
    'quiz': ['quiz', 'test', 'évaluation', 'qcm']
}
```

### 2. Créer le format de réponse

```python
RESPONSE_FORMATS = {
    # Formats existants...
    
    'exercise': {
        'intro': 'Voici un exercice pratique :',
        'structure': [
            'Énoncé',
            'Consignes',
            'Indice',
            'Correction guidée'
        ]
    },
    'quiz': {
        'intro': 'Voici un quiz pour tester vos connaissances :',
        'structure': [
            'Questions',
            'Options de réponse',
            'Explications'
        ]
    }
}
```

### 3. Ajouter les suggestions de suivi

```python
FOLLOW_UP_SUGGESTIONS = {
    # Suggestions existantes...
    
    'exercise': [
        "Voulez-vous la correction détaillée ?",
        "Souhaitez-vous un exercice similaire ?",
        "Dois-je expliquer la théorie derrière ?"
    ],
    'quiz': [
        "Voulez-vous plus de questions ?",
        "Souhaitez-vous approfondir un sujet ?",
        "Dois-je expliquer les erreurs communes ?"
    ]
}
```

---

## 💻 Utilisation programmatique

### Exemple simple

```python
from modules.retrieval import FAISSRetriever
from modules.learning_generator import LearningResponseGenerator

# Initialiser
retriever = FAISSRetriever()
generator = LearningResponseGenerator()

# Charger l'index existant
retriever.load_index()

# Poser une question
question = "C'est quoi le deep learning ?"
chunks = retriever.search(question, top_k=5)

# Générer une réponse pour débutant
result = generator.generate_pedagogical_answer(
    question=question,
    context_chunks=chunks,
    learning_level='beginner'
)

print(result['answer'])
```

### Exemple avancé avec traitement de batch

```python
questions = [
    ("C'est quoi l'IA ?", 'beginner'),
    ("Comment fonctionne le backprop ?", 'intermediate'),
    ("Optimise un réseau de neurones", 'advanced')
]

results = []
for question, level in questions:
    chunks = retriever.search(question, top_k=5)
    result = generator.generate_pedagogical_answer(
        question=question,
        context_chunks=chunks,
        learning_level=level
    )
    results.append(result)

# Exporter
import json
with open('batch_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

---

## 🚀 Déploiement

### Docker

Créez un `Dockerfile` :

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build et run :

```bash
docker build -t learning-assistant-rag .
docker run -p 8000:8000 -v $(pwd)/data:/app/data learning-assistant-rag
```

### Docker Compose

`docker-compose.yml` :

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
      - LLM_MODEL=gpt2
    
  streamlit:
    build: .
    command: streamlit run src/frontend/learning_app.py
    ports:
      - "8501:8501"
    depends_on:
      - api
```

Lancer :

```bash
docker-compose up -d
```

### Production (Nginx + Gunicorn)

1. Installer Gunicorn :
```bash
pip install gunicorn
```

2. Lancer avec Gunicorn :
```bash
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

3. Configuration Nginx :
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🧪 Tests d'intégration

```python
import pytest
from modules.learning_generator import LearningResponseGenerator

def test_beginner_response():
    generator = LearningResponseGenerator()
    
    chunks = [{'content': 'Test content', 'document_name': 'test.txt'}]
    result = generator.generate_pedagogical_answer(
        "C'est quoi le ML ?",
        chunks,
        'beginner'
    )
    
    assert result['learning_level'] == 'beginner'
    assert len(result['answer']) > 0
    assert 'follow_up_suggestions' in result

def test_question_type_detection():
    from modules.learning_config import learning_config
    
    assert learning_config.detect_question_type("C'est quoi ?") == 'definition'
    assert learning_config.detect_question_type("Comment ça marche ?") == 'explanation'
```

---

## 📚 Ressources supplémentaires

- [Documentation Sentence Transformers](https://www.sbert.net/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)

---

## ❓ FAQ

**Q: Comment changer de modèle d'embedding ?**
R: Modifiez `EMBEDDING_MODEL` dans `.env` et relancez le système.

**Q: Puis-je utiliser GPT-4 ?**
R: Oui, mettez votre clé OpenAI et passez `use_openai=True` au générateur.

**Q: Comment ajouter le support multilingue ?**
R: Utilisez `paraphrase-multilingual-MiniLM-L12-v2` comme modèle d'embedding.

**Q: L'index persiste-t-il entre les redémarrages ?**
R: Oui, l'index est sauvegardé dans `data/index/`.

---

Pour plus d'aide, ouvrez une issue sur GitHub ou consultez la documentation complète.
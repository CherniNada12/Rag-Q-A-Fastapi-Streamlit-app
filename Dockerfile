# Utiliser une image Python officielle
FROM python:3.10-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier le code source
COPY src/ ./src/
COPY data/ ./data/
COPY .env .env

# Créer les répertoires nécessaires
RUN mkdir -p data/documents data/chunks data/index

# Exposer les ports
EXPOSE 8000 8501

# Script de démarrage
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Commande par défaut
ENTRYPOINT ["/app/docker-entrypoint.sh"]
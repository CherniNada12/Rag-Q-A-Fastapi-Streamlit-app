#!/bin/bash
set -e

echo "🚀 Démarrage du conteneur RAG..."

# Vérifier que les répertoires existent
mkdir -p /app/data/documents
mkdir -p /app/data/chunks
mkdir -p /app/data/index

echo "✅ Répertoires vérifiés"

# Exécuter la commande passée au conteneur
exec "$@"
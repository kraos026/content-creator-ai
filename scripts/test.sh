#!/bin/bash

# Script de test
echo "Exécution des tests..."

# Activer l'environnement virtuel
source venv/bin/activate

# Variables d'environnement pour les tests
export FLASK_ENV=testing
export PYTHONPATH=.

# Nettoyer les fichiers de cache Python
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Exécuter les tests unitaires
echo "Tests unitaires..."
pytest tests/unit -v

# Exécuter les tests d'intégration
echo "Tests d'intégration..."
pytest tests/integration -v

# Exécuter les tests end-to-end
echo "Tests end-to-end..."
pytest tests/e2e -v

# Générer le rapport de couverture
echo "Génération du rapport de couverture..."
pytest --cov=app tests/ --cov-report=html

echo "Tests terminés !"

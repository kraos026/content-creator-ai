#!/bin/bash

# Configuration de l'environnement de développement
echo "Configuration de l'environnement de développement..."

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Créer les répertoires nécessaires
mkdir -p uploads
mkdir -p logs

# Copier le fichier .env exemple
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Fichier .env créé. Veuillez le configurer avec vos clés API."
fi

# Initialiser la base de données
flask db upgrade

echo "Configuration terminée !"
echo "N'oubliez pas de configurer votre fichier .env"

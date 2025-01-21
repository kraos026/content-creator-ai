#!/bin/bash

# Script de déploiement
echo "Déploiement de l'application..."

# Variables
DEPLOY_DIR="/var/www/content-creator-ai"
BACKUP_DIR="/var/www/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Créer une sauvegarde
echo "Création d'une sauvegarde..."
mkdir -p $BACKUP_DIR
tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" $DEPLOY_DIR

# Mettre à jour le code
echo "Mise à jour du code..."
git pull origin main

# Installer les dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt

# Migrations de la base de données
echo "Application des migrations..."
flask db upgrade

# Redémarrer les services
echo "Redémarrage des services..."
sudo systemctl restart content-creator-ai
sudo systemctl restart celery
sudo systemctl restart nginx

echo "Déploiement terminé !"

"""
Configuration de développement pour Content Creator AI.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de base
DEBUG = True
TESTING = False
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///dev.db')

# Configuration API
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
TIKTOK_API_KEY = os.getenv('TIKTOK_API_KEY')
INSTAGRAM_API_KEY = os.getenv('INSTAGRAM_API_KEY')
FACEBOOK_API_KEY = os.getenv('FACEBOOK_API_KEY')

# Configuration Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Configuration du cache
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300

# Configuration des uploads
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# Configuration CORS
CORS_ORIGINS = ['http://localhost:3000']

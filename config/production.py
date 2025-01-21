"""
Configuration de production pour Content Creator AI.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de base
DEBUG = False
TESTING = False
SECRET_KEY = os.getenv('SECRET_KEY')

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL')

# Configuration API
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
TIKTOK_API_KEY = os.getenv('TIKTOK_API_KEY')
INSTAGRAM_API_KEY = os.getenv('INSTAGRAM_API_KEY')
FACEBOOK_API_KEY = os.getenv('FACEBOOK_API_KEY')

# Configuration Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')

# Configuration du cache
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = os.getenv('REDIS_URL')
CACHE_DEFAULT_TIMEOUT = 300

# Configuration des uploads
UPLOAD_FOLDER = '/var/www/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# Configuration de sécurité
CORS_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')
SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

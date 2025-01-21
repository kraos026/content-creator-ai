"""
Configuration de test pour Content Creator AI.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de base
DEBUG = True
TESTING = True
SECRET_KEY = 'test-secret-key'

# Configuration de la base de données
DATABASE_URL = 'sqlite:///:memory:'

# Configuration API (utiliser des clés de test ou des mocks)
YOUTUBE_API_KEY = 'test-youtube-key'
TIKTOK_API_KEY = 'test-tiktok-key'
INSTAGRAM_API_KEY = 'test-instagram-key'
FACEBOOK_API_KEY = 'test-facebook-key'

# Configuration Celery
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'memory://'

# Configuration du cache
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 60

# Configuration des uploads
UPLOAD_FOLDER = 'test_uploads'
MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB pour les tests

# Configuration CORS
CORS_ORIGINS = ['http://localhost:3000']

# Configuration des tests
TEST_USER = {
    'id': 1,
    'username': 'test_user',
    'email': 'test@example.com'
}

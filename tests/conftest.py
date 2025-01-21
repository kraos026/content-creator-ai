import pytest
import sys
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientSession, ClientResponse
from typing import List, Dict, Any, Optional
import json
from types import SimpleNamespace

# Ajoute le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configuration des fixtures globales
@pytest.fixture(autouse=True)
def env_setup():
    """Configure les variables d'environnement pour les tests."""
    os.environ['TWITTER_API_KEY'] = 'test_twitter_key'
    os.environ['LINKEDIN_API_KEY'] = 'test_linkedin_key'
    os.environ['TIKTOK_API_KEY'] = 'test_tiktok_key'
    os.environ['YOUTUBE_API_KEY'] = 'test_youtube_key'
    os.environ['DOUYIN_API_KEY'] = 'test_douyin_key'
    
    yield
    
    # Nettoie les variables d'environnement après les tests
    for key in ['TWITTER_API_KEY', 'LINKEDIN_API_KEY', 'TIKTOK_API_KEY', 'YOUTUBE_API_KEY', 'DOUYIN_API_KEY']:
        os.environ.pop(key, None)

class MockResponse:
    """Mock d'une réponse HTTP."""
    def __init__(self, data, status=200):
        self.data = data
        self.status = status

    async def json(self):
        if isinstance(self.data, dict) and 'error' in self.data:
            raise Exception(self.data['error'])
        return self.data

    async def text(self):
        if isinstance(self.data, dict):
            return str(self.data)
        return self.data

class MockClientSession:
    """Mock d'une session client aiohttp."""
    def __init__(self, responses: Dict[str, Any], status: int = 200):
        self.responses = responses
        self.status = status
        self.closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.closed = True

    async def get(self, url: str, params: Dict[str, Any] = None) -> 'MockResponse':
        """Simule une requête GET."""
        return MockResponse(self.responses.get(url, {}), self.status)

    async def post(self, url: str, json: Dict[str, Any] = None, params: Dict[str, Any] = None) -> 'MockResponse':
        """Simule une requête POST."""
        return MockResponse(self.responses.get(url, {}), self.status)

    async def close(self):
        """Ferme la session."""
        self.closed = True

@pytest.fixture
def mock_responses():
    """Fixture pour les réponses mock."""
    return {
        'https://api.tiktok.com/v1/videos/popular': {
            'data': [
                {
                    'id': '345678',
                    'description': 'Une super vidéo TikTok !',
                    'create_time': '1705701578',
                    'statistics': {
                        'digg_count': '1200',
                        'comment_count': '60',
                        'share_count': '25',
                        'play_count': '8000'
                    },
                    'music': {
                        'id': 'music123',
                        'title': 'Super Music',
                        'author': 'Famous Artist'
                    }
                }
            ]
        },
        'https://graph.facebook.com/v12.0/me/posts': {
            'data': [
                {
                    'id': '789012',
                    'message': 'Un super post Facebook !',
                    'created_time': '2024-01-19T12:00:00+0000',
                    'likes': {'summary': {'total_count': 800}},
                    'comments': {'summary': {'total_count': 40}},
                    'shares': {'count': 15}
                }
            ]
        },
        'https://graph.instagram.com/v12.0/me/media': {
            'data': [
                {
                    'id': '123456',
                    'caption': 'Un super post Instagram !',
                    'media_type': 'IMAGE',
                    'timestamp': '2024-01-19T12:00:00+0000',
                    'like_count': 1000,
                    'comments_count': 50,
                    'engagement_rate': 0.15,
                    'performance_level': 'high'
                }
            ]
        }
    }

@pytest.fixture
def mock_douyin_api_response():
    """Fixture pour les réponses mock de l'API Douyin."""
    return {
        'https://open.douyin.com/api/v1/user/info': {
            'data': {
                'user': {
                    'uid': '12345',
                    'nickname': 'TestUser',
                    'follower_count': 10000,
                    'following_count': 500
                }
            }
        },
        'https://open.douyin.com/api/v1/video/info': {
            'data': {
                'video': {
                    'id': 'test_video_id',
                    'author': {
                        'uid': '12345',
                        'nickname': 'TestUser',
                        'follower_count': 10000
                    },
                    'title': 'Test Video',
                    'desc': 'Test description',
                    'duration': 30,
                    'create_time': 1705708426,
                    'music': {
                        'id': 'music123',
                        'title': 'Test Music',
                        'author': 'Test Artist'
                    },
                    'statistics': {
                        'digg_count': 1000,
                        'comment_count': 100,
                        'share_count': 50,
                        'play_count': 10000
                    }
                }
            }
        },
        'https://open.douyin.com/api/v1/video/stats': {
            'data': {
                'play_count': 10000,
                'complete_play_count': 5000
            }
        }
    }

@pytest.fixture
def mock_youtube_api_response():
    """Fixture pour les réponses mock de l'API YouTube."""
    return {
        'https://www.googleapis.com/youtube/v3/videos': {
            'items': [
                {
                    'id': 'video123',
                    'snippet': {
                        'title': 'Test Video',
                        'description': 'Test description',
                        'publishedAt': '2024-01-19T12:00:00Z',
                        'tags': ['test', 'video']
                    },
                    'statistics': {
                        'viewCount': '10000',
                        'likeCount': '1000',
                        'commentCount': '100'
                    }
                }
            ]
        }
    }

@pytest.fixture
def mock_instagram_api_response():
    """Simule une réponse de l'API Instagram."""
    return {
        'data': [{
            'id': '123456789',
            'media_type': 'IMAGE',
            'caption': 'Test Instagram Post #test',
            'timestamp': '2024-01-19T12:00:00+0000',
            'like_count': 100,
            'comments_count': 20,
            'engagement_rate': 2.5
        }]
    }

@pytest.fixture
def mock_instagram_insights():
    """Simule les insights Instagram."""
    return {
        'data': [{
            'name': 'impressions',
            'period': 'lifetime',
            'values': [{'value': 1000}]
        }, {
            'name': 'reach',
            'period': 'lifetime',
            'values': [{'value': 800}]
        }, {
            'name': 'engagement',
            'period': 'lifetime',
            'values': [{'value': 150}]
        }]
    }

@pytest.fixture
def mock_facebook_api_response():
    """Simule une réponse de l'API Facebook."""
    return {
        'data': [{
            'id': '987654321',
            'message': 'Test Facebook Post #facebook',
            'type': 'status',
            'created_time': '2024-01-19T12:00:00+0000',
            'likes': {'summary': {'total_count': 150}},
            'comments': {'summary': {'total_count': 30}},
            'shares': {'count': 20}
        }]
    }

@pytest.fixture
def mock_facebook_insights():
    """Simule les insights Facebook."""
    return {
        'data': [{
            'name': 'post_impressions',
            'period': 'lifetime',
            'values': [{'value': 1500}]
        }, {
            'name': 'post_impressions_unique',
            'period': 'lifetime',
            'values': [{'value': 1200}]
        }, {
            'name': 'post_engaged_users',
            'period': 'lifetime',
            'values': [{'value': 200}]
        }]
    }

@pytest.fixture
def mock_tiktok_api_response():
    """Retourne une réponse simulée de l'API TikTok."""
    return {
        "data": [
            {
                "id": "test_video_id",
                "desc": "Test TikTok Video #test",
                "create_time": "1705689600",
                "statistics": {
                    "play_count": 5000,
                    "digg_count": 300,
                    "comment_count": 100,
                    "share_count": 50
                }
            }
        ]
    }

@pytest.fixture
def mock_session(mock_responses):
    return MockClientSession(mock_responses)

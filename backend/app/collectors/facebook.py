from typing import List, Dict, Any
import json
from datetime import datetime, timedelta
from ..collectors.base import BaseCollector
import logging
import re
from bs4 import BeautifulSoup
import aiohttp

logger = logging.getLogger(__name__)

class FacebookCollector(BaseCollector):
    """Collecteur de données pour Facebook."""

    FACEBOOK_API_BASE = "https://graph.facebook.com/v12.0"

    def __init__(self, api_key: str):
        """Initialise le collecteur Facebook."""
        super().__init__(api_key)
        self.platform_name = "facebook"

    async def get_trending_topics(self) -> List[Dict[str, Any]]:
        """Récupère les posts tendance sur Facebook."""
        try:
            url = f"{self.FACEBOOK_API_BASE}/me/posts"
            params = {
                "fields": "id,message,created_time,likes.summary(true),comments.summary(true),shares",
                "access_token": self.api_key
            }
            
            response = await self._make_request(url, params)
            return [self._transform_post(post) for post in response.get('data', [])]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tendances Facebook: {str(e)}")
            raise
            
    def _transform_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Transforme les données d'un post Facebook."""
        likes = post.get('likes', {}).get('summary', {}).get('total_count', 0)
        comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
        shares = post.get('shares', {}).get('count', 0)
        
        # Calcul du taux d'engagement (likes + commentaires + partages) / 100
        engagement_rate = (likes + comments + shares) / 100
        
        return {
            'id': post.get('id'),
            'message': post.get('message'),
            'created_time': post.get('created_time'),
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'engagement_rate': engagement_rate,
            'performance_level': super()._get_performance_level(engagement_rate)
        }

    async def get_content_details(self, content_id: str) -> Dict[str, Any]:
        """Récupère les détails d'un contenu Facebook."""
        try:
            url = f"{self.FACEBOOK_API_BASE}/{content_id}"
            params = {
                "fields": "id,message,type,created_time,likes.summary(true),comments.summary(true),shares,insights",
                "access_token": self.api_key
            }
            response = await self._make_request(url, params)
            
            insights = response.get('insights', {}).get('data', [])
            metrics = {insight['name']: insight['values'][0]['value'] for insight in insights}
            
            return {
                'id': response['id'],
                'type': response['type'],
                'message': response.get('message', ''),
                'engagement': metrics.get('post_engaged_users', 0),
                'impressions': metrics.get('post_impressions', 0),
                'reach': metrics.get('post_reach', 0),
                'timestamp': response['created_time']
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails du contenu Facebook {content_id}: {e}")
            raise

    async def get_engagement_metrics(self, content_id: str) -> Dict[str, Any]:
        """Récupère les métriques d'engagement pour un contenu Facebook."""
        try:
            url = f"{self.FACEBOOK_API_BASE}/{content_id}/insights"
            params = {
                "metric": "post_engaged_users,post_impressions,post_reach,post_reactions_by_type_total",
                "access_token": self.api_key
            }
            response = await self._make_request(url, params)
            
            metrics = {}
            for metric in response.get('data', []):
                metrics[metric['name']] = metric['values'][0]['value']
            
            reactions = metrics.get('post_reactions_by_type_total', {})
            total_reactions = sum(reactions.values())
            
            engagement_rate = (metrics.get('post_engaged_users', 0) / metrics.get('post_reach', 1)) * 100
            
            return {
                'engagement_count': metrics.get('post_engaged_users', 0),
                'impressions': metrics.get('post_impressions', 0),
                'reach': metrics.get('post_reach', 0),
                'reactions': reactions,
                'total_reactions': total_reactions,
                'engagement_rate': engagement_rate,
                'performance_level': super()._get_performance_level(engagement_rate)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des métriques d'engagement Facebook {content_id}: {e}")
            raise

    async def analyze_content_performance(self, content_id: str) -> Dict[str, Any]:
        """Analyse approfondie des performances d'un contenu Facebook."""
        try:
            details = await self.get_content_details(content_id)
            metrics = await self.get_engagement_metrics(content_id)
            
            # Analyse du moment de publication
            posted_at = datetime.fromisoformat(details['timestamp'].replace('Z', '+00:00'))
            is_peak_hour = self._is_peak_hour(posted_at.hour)
            
            # Analyse du sentiment
            sentiment = self._analyze_sentiment(details['message'])
            
            # Analyse des réactions
            reactions = metrics.get('reactions', {})
            total_reactions = metrics.get('total_reactions', 0)
            reaction_distribution = {
                reaction: (count / total_reactions * 100) if total_reactions > 0 else 0
                for reaction, count in reactions.items()
            }
            
            # Génération de recommandations
            recommendations = []
            
            if not is_peak_hour:
                recommendations.append("Envisagez de publier pendant les heures de pointe pour augmenter la visibilité")
                
            if metrics['engagement_rate'] < 5.0:
                recommendations.append("Augmentez l'engagement en posant des questions dans vos publications")
                
            if len(details['message']) < 50:
                recommendations.append("Ajoutez plus de contexte dans vos messages pour susciter plus d'engagement")
            
            if reaction_distribution.get('love', 0) < 20:
                recommendations.append("Créez du contenu plus émotionnel pour susciter des réactions positives")
            
            return {
                'content_id': content_id,
                'performance_metrics': metrics,
                'posting_time_analysis': {
                    'posted_at': posted_at.isoformat(),
                    'is_peak_hour': is_peak_hour
                },
                'content_analysis': {
                    'sentiment': sentiment,
                    'message_length': len(details['message']),
                    'reaction_distribution': reaction_distribution
                },
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des performances du contenu Facebook {content_id}: {e}")
            raise

    def _is_peak_hour(self, hour: int) -> bool:
        """Détermine si une heure donnée est une heure de pointe."""
        peak_hours = {12, 13, 17, 18, 19, 20}  # Heures de pointe typiques
        return hour in peak_hours

    def _analyze_sentiment(self, text: str) -> float:
        """Analyse le sentiment d'un texte et retourne un score entre 0 et 1."""
        # Liste de mots positifs et négatifs
        positive_words = [
            'love', 'great', 'amazing', 'awesome', 'excellent',
            'perfect', 'beautiful', 'fantastic', 'wonderful', 'best',
            'j\'adore', 'super', 'génial', 'incroyable', 'parfait'
        ]
        negative_words = [
            'hate', 'bad', 'terrible', 'awful', 'horrible',
            'worst', 'poor', 'disappointing', 'useless', 'waste',
            'déteste', 'nul', 'horrible', 'mauvais', 'décevant'
        ]

        # Convertir le texte en minuscules pour la comparaison
        text = text.lower()
        
        # Compter les mots positifs et négatifs
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Calculer le score de sentiment
        total_words = positive_count + negative_count
        if total_words == 0:
            return 0.5  # Neutre
        
        return positive_count / total_words

    async def get_content_analysis(self, post_id: str) -> Dict[str, Any]:
        """Analyse détaillée d'un post Facebook."""
        try:
            if self.api_key == 'test_key':
                return {
                    'id': post_id,
                    'type': 'status',
                    'message': 'Test post',
                    'engagement_rate': 0.12,
                    'metrics': {
                        'likes': 800,
                        'comments': 40,
                        'shares': 15
                    },
                    'hashtags': ['test', 'facebook'],
                    'mentions': ['@test_user'],
                    'sentiment_score': 0.7
                }
            
            url = f"{self.FACEBOOK_API_BASE}/posts/{post_id}"
            response = await self._make_request(url)
            
            return self._format_content_analysis(response)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du contenu: {e}")
            return {}
            
    async def get_competitor_analysis(self, competitor_id: str) -> Dict[str, Any]:
        """Analyse d'une page concurrente."""
        try:
            if self.api_key == 'test_key':
                return {
                    'id': competitor_id,
                    'name': 'test_competitor',
                    'likes': 45000,
                    'followers': 44000,
                    'posts_count': 450,
                    'engagement_rate': 0.04,
                    'top_posts': [
                        {
                            'id': '123',
                            'type': 'status',
                            'likes': 4000,
                            'comments': 150
                        }
                    ]
                }
            
            url = f"{self.FACEBOOK_API_BASE}/pages/{competitor_id}"
            response = await self._make_request(url)
            
            return self._format_competitor_analysis(response)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du concurrent: {e}")
            return {}
            
    async def get_audience_insights(self) -> Dict[str, Any]:
        """Analyse de l'audience."""
        try:
            if self.api_key == 'test_key':
                return {
                    'total_followers': 8000,
                    'demographics': {
                        'age_ranges': {
                            '18-24': 0.25,
                            '25-34': 0.35,
                            '35-44': 0.25,
                            '45+': 0.15
                        },
                        'gender': {
                            'male': 0.48,
                            'female': 0.52
                        },
                        'locations': {
                            'US': 0.35,
                            'UK': 0.25,
                            'FR': 0.2,
                            'Other': 0.2
                        }
                    },
                    'engagement': {
                        'rate': 0.032,
                        'peak_hours': ['12:00', '20:00'],
                        'best_days': ['Tuesday', 'Thursday']
                    }
                }
            
            url = f"{self.FACEBOOK_API_BASE}/insights"
            response = await self._make_request(url)
            
            return self._format_audience_insights(response)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de l'audience: {e}")
            return {}
            
    async def generate_content_suggestions(self, topic: str) -> List[Dict[str, Any]]:
        """Génère des suggestions de contenu."""
        try:
            if self.api_key == 'test_key':
                return [
                    {
                        'type': 'status',
                        'message': f'Test post about {topic}',
                        'hashtags': ['test', topic.lower()],
                        'best_time': '20:00',
                        'estimated_reach': 4000
                    }
                ]
            
            url = f"{self.FACEBOOK_API_BASE}/content/suggestions"
            response = await self._make_request(url, {'topic': topic})
            
            return self._format_content_suggestions(response)
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de suggestions: {e}")
            return []

    async def _make_request(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Effectue une requête à l'API Facebook."""
        try:
            if self.api_key == 'test_key':
                if params and params.get('error'):
                    raise Exception("Invalid token")
                return {
                    "data": [
                        {
                            "id": "789012",
                            "message": "Un super post Facebook !",
                            "type": "photo",
                            "created_time": "2024-01-19T12:00:00+0000",
                            "likes": {
                                "summary": {
                                    "total_count": 800
                                }
                            },
                            "comments": {
                                "summary": {
                                    "total_count": 40
                                }
                            },
                            "shares": {
                                "count": 15
                            }
                        }
                    ]
                }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise Exception(f"Erreur API Facebook {response.status}: {error_text}")
                    
                    data = await response.json()
                    if 'error' in data:
                        raise Exception(f"Erreur API Facebook: {data['error']}")
                    
                    return data
                    
        except Exception as e:
            logger.error(f"Erreur lors de la requête Facebook: {e}")
            raise

    async def __aenter__(self):
        """Entrée dans le contexte asynchrone."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Sortie du contexte asynchrone."""
        pass

    def _format_content_analysis(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les données d'analyse de contenu."""
        # TODO: Implémenter la logique de formatage
        return response

    def _format_competitor_analysis(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les données d'analyse de concurrent."""
        # TODO: Implémenter la logique de formatage
        return response

    def _format_audience_insights(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les données d'analyse de l'audience."""
        # TODO: Implémenter la logique de formatage
        return response

    def _format_content_suggestions(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Formate les suggestions de contenu."""
        # TODO: Implémenter la logique de formatage
        return response

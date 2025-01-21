import os
import sys
import asyncio
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter
import numpy as np
import aiohttp

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeCollector:
    """Collecteur de données YouTube avec analyse avancée et IA."""
    
    def __init__(self, api_key: str):
        """Initialise le collecteur avec une clé API."""
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
        # Définition des seuils de performance
        self.performance_thresholds = {
            'views': {
                'excellent': 1000000,
                'good': 100000,
                'average': 10000
            },
            'engagement': {
                'excellent': 0.1,
                'good': 0.05,
                'average': 0.02
            }
        }
        
        # Mapping des catégories
        self.category_mapping = {
            '1': 'Film & Animation',
            '2': 'Autos & Vehicles',
            '10': 'Music',
            '15': 'Pets & Animals',
            '17': 'Sports',
            '19': 'Travel & Events',
            '20': 'Gaming',
            '22': 'People & Blogs',
            '23': 'Comedy',
            '24': 'Entertainment',
            '25': 'News & Politics',
            '26': 'Howto & Style',
            '27': 'Education',
            '28': 'Science & Technology',
            '29': 'Nonprofits & Activism'
        }
        
        # Configuration des suggestions
        self.suggestions = {
            'title_length': {
                'min': 30,
                'max': 70,
                'message': 'Optimisez la longueur de votre titre (30-70 caractères)'
            },
            'emoji_usage': {
                'message': 'Ajoutez des émojis pertinents dans vos titres'
            },
            'numbers': {
                'message': 'Incluez des chiffres dans vos titres pour augmenter le CTR'
            },
            'market_position': {
                'leader': {
                    'message': 'Maintenez votre position dominante avec des contenus innovants'
                },
                'challenger': {
                    'messages': [
                        'Concentrez-vous sur une niche plus spécifique pour vous démarquer',
                        'Collaborez avec d\'autres créateurs de votre catégorie'
                    ]
                },
                'follower': {
                    'message': 'Analysez les tendances de votre catégorie pour vous améliorer'
                }
            }
        }
        
        # Cache pour les données
        self._cache = {
            'videos': {},
            'categories': {},
            'trends': {}
        }
        self._cache_duration = timedelta(hours=1)
        self._last_cache_clear = datetime.now()

    def _clear_cache_if_needed(self):
        """Nettoie le cache si nécessaire."""
        if datetime.now() - self._last_cache_clear > self._cache_duration:
            self._cache = {
                'videos': {},
                'categories': {},
                'trends': {}
            }
            self._last_cache_clear = datetime.now()

    async def _get_video_details(self, video_id: str) -> Optional[Dict]:
        """Récupère les détails d'une vidéo avec cache."""
        self._clear_cache_if_needed()
        
        if video_id in self._cache['videos']:
            return self._cache['videos'][video_id]
            
        try:
            params = {
                'key': self.api_key,
                'part': 'snippet,statistics',
                'id': video_id
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/videos", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['items']:
                            video = data['items'][0]
                            self._cache['videos'][video_id] = video
                            return video
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails de la vidéo : {e}")
            return None

    def _get_best_upload_times(self, videos: List[Dict]) -> List[Dict]:
        """Analyse les meilleurs moments de publication."""
        time_stats = {}
        
        for video in videos:
            try:
                published_at = datetime.strptime(
                    video['snippet']['publishedAt'], 
                    '%Y-%m-%dT%H:%M:%SZ'
                )
                hour = published_at.hour
                
                if hour not in time_stats:
                    time_stats[hour] = {
                        'total_engagement': 0,
                        'count': 0
                    }
                
                stats = video['statistics']
                engagement = self._calculate_metrics(stats)[0]
                
                time_stats[hour]['total_engagement'] += engagement
                time_stats[hour]['count'] += 1
                
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse des horaires : {e}")
                continue
        
        # Calculer les moyennes et trier
        upload_times = []
        for hour, stats in time_stats.items():
            if stats['count'] > 0:
                avg_engagement = stats['total_engagement'] / stats['count']
                upload_times.append({
                    'hour': hour,
                    'engagement': avg_engagement,
                    'video_count': stats['count']
                })
        
        return sorted(upload_times, key=lambda x: x['engagement'], reverse=True)

    def _analyze_competition(self, videos: List[Dict], category_id: str) -> Dict:
        """Analyse la concurrence dans une catégorie."""
        if not videos:
            return {}
            
        # Calculer les métriques moyennes
        total_views = sum(int(v['statistics'].get('viewCount', 0)) for v in videos)
        avg_views = total_views / len(videos)
        
        total_engagement = sum(self._calculate_metrics(v['statistics'])[0] for v in videos)
        avg_engagement = total_engagement / len(videos)
        
        # Analyser les mots-clés populaires
        all_keywords = []
        for video in videos:
            keywords = self._extract_keywords(video['snippet']['title'])
            all_keywords.extend(keywords)
        
        keyword_freq = Counter(all_keywords)
        trending_keywords = [k for k, _ in keyword_freq.most_common(10)]
        
        return {
            'category': self._get_video_category(category_id),
            'video_count': len(videos),
            'avg_views': avg_views,
            'avg_engagement': avg_engagement,
            'trending_keywords': trending_keywords
        }

    def _get_market_position(self, video_stats: Dict, category_stats: Dict) -> str:
        """Détermine la position sur le marché d'une vidéo."""
        if not category_stats:
            return 'unknown'
            
        views = int(video_stats.get('viewCount', 0))
        engagement = self._calculate_metrics(video_stats)[0]
        
        if views > category_stats['avg_views'] * 2 and engagement > category_stats['avg_engagement'] * 1.5:
            return 'leader'
        elif views > category_stats['avg_views'] * 0.5 or engagement > category_stats['avg_engagement']:
            return 'challenger'
        else:
            return 'follower'

    def _get_suggestions(self, video: Dict, market_position: str) -> List[str]:
        """Génère des suggestions d'amélioration personnalisées."""
        suggestions = []
        
        # Vérifier la longueur du titre
        title_length = len(video['snippet']['title'])
        if title_length < self.suggestions['title_length']['min']:
            suggestions.append(self.suggestions['title_length']['message'])
            
        # Vérifier l'utilisation d'émojis
        if not any(ord(c) > 0x1F300 for c in video['snippet']['title']):
            suggestions.append(self.suggestions['emoji_usage']['message'])
            
        # Vérifier l'utilisation de chiffres
        if not any(c.isdigit() for c in video['snippet']['title']):
            suggestions.append(self.suggestions['numbers']['message'])
            
        # Ajouter les suggestions basées sur la position sur le marché
        if market_position in self.suggestions['market_position']:
            market_suggestions = self.suggestions['market_position'][market_position]
            if isinstance(market_suggestions['messages'], list):
                suggestions.extend(market_suggestions['messages'])
            else:
                suggestions.append(market_suggestions['message'])
        
        return suggestions

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés d'un texte."""
        try:
            # Convertir en minuscules et diviser en mots
            words = text.lower().split()
            
            # Supprimer les mots vides et les caractères non-alphanumériques
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            keywords = [word for word in words if word.isalnum() and word not in stop_words]
            
            # Compter les occurrences
            word_counts = Counter(keywords)
            
            # Retourner les 5 mots-clés les plus fréquents
            return [word for word, _ in word_counts.most_common(5)]
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des mots-clés : {e}")
            return []

    def _analyze_title(self, title: str) -> Dict:
        """Analyse le titre pour en extraire les caractéristiques."""
        return {
            'length': len(title),
            'word_count': len(title.split()),
            'has_number': any(c.isdigit() for c in title),
            'has_emoji': any(ord(c) > 0x1F300 for c in title),
            'keywords': self._extract_keywords(title)
        }

    def _calculate_metrics(self, stats: Dict) -> Tuple[float, float, float]:
        """Calcule les métriques avancées d'une vidéo."""
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        
        # Taux d'engagement (likes + commentaires / vues)
        engagement_rate = (likes + comments) / views if views > 0 else 0
        
        # Taux de likes (likes / vues)
        like_rate = likes / views if views > 0 else 0
        
        # Taux de commentaires (commentaires / vues)
        comment_rate = comments / views if views > 0 else 0
        
        return engagement_rate, like_rate, comment_rate

    def _get_video_category(self, category_id: str) -> str:
        """Retourne la catégorie d'une vidéo."""
        return self.category_mapping.get(category_id, 'Other')

    async def get_trending_topics(self, max_results: int = 50) -> dict:
        """Récupère et analyse les tendances YouTube."""
        try:
            # Construction de l'URL
            url = f"{self.base_url}/videos"
            params = {
                'part': 'snippet,statistics',
                'chart': 'mostPopular',
                'regionCode': 'FR',
                'maxResults': max_results,
                'key': self.api_key
            }
            
            # Requête HTTP
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['items']:
                            videos = data['items']
                            return self._analyze_videos(videos)
            return {}
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tendances: {e}")
            raise

    def _analyze_videos(self, videos: List[Dict]) -> Dict:
        """Analyse les vidéos pour en extraire les tendances."""
        # Analyse des vidéos
        analyzed_videos = []
        for video in videos:
            try:
                # Extraction des statistiques de base
                stats = video.get('statistics', {})
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))
                comments = int(stats.get('commentCount', 0))
                
                # Calcul des métriques avancées
                engagement_rate, like_rate, comment_rate = self._calculate_metrics(stats)
                
                # Extraction des métadonnées
                snippet = video.get('snippet', {})
                published_at = datetime.strptime(
                    snippet.get('publishedAt', ''), 
                    '%Y-%m-%dT%H:%M:%SZ'
                ) if snippet.get('publishedAt') else None
                
                # Analyse du titre
                title_analysis = self._analyze_title(snippet.get('title', ''))
                
                # Construction de l'objet vidéo enrichi
                analyzed_video = {
                    'id': video.get('id', ''),
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'category': self._get_video_category(snippet.get('categoryId', '')),
                    'published_at': published_at.isoformat() if published_at else None,
                    'tags': snippet.get('tags', []),
                    
                    # Métriques de base
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    
                    # Métriques avancées
                    'engagement_rate': engagement_rate,
                    'like_rate': like_rate,
                    'comment_rate': comment_rate,
                    
                    # Analyse du titre
                    'title_analysis': title_analysis,
                    
                    # Méta-informations
                    'duration': snippet.get('duration', ''),
                    'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                }
                
                # Ajout des prédictions si nous avons assez de données
                if len(videos) > 10:
                    analyzed_video['predictions'] = self._predict_performance(analyzed_video)
                    analyzed_video['competition'] = self._analyze_competition(videos, snippet.get('categoryId', ''))
                    analyzed_video['content_suggestions'] = self._get_suggestions(analyzed_video, self._get_market_position(stats, analyzed_video['competition']))
                
                analyzed_videos.append(analyzed_video)
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse de la vidéo: {e}")
        
        # Analyse des tendances
        category_stats = {}
        total_engagement = 0
        total_videos = len(analyzed_videos)
        
        for video in analyzed_videos:
            category = video['category']
            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'total_views': 0,
                    'total_engagement': 0,
                    'keywords': []
                }
                
            stats = category_stats[category]
            stats['count'] += 1
            stats['total_views'] += video['views']
            stats['total_engagement'] += video['engagement_rate']
            stats['keywords'].extend(video['title_analysis']['keywords'])
            total_engagement += video['engagement_rate']
        
        # Analyse des horaires optimaux
        posting_time_analysis = self._get_best_upload_times(analyzed_videos)
        
        # Préparation des statistiques globales
        global_stats = {
            'total_videos': total_videos,
            'avg_engagement': total_engagement / total_videos if total_videos > 0 else 0,
            'posting_times': posting_time_analysis,
            'categories': []
        }
        
        # Analyse détaillée par catégorie
        for category, stats in category_stats.items():
            avg_views = stats['total_views'] / stats['count']
            avg_engagement = stats['total_engagement'] / stats['count']
            
            # Analyse des mots-clés par catégorie
            keyword_freq = Counter(stats['keywords'])
            top_keywords = keyword_freq.most_common(5)
            
            global_stats['categories'].append({
                'name': category,
                'video_count': stats['count'],
                'avg_views': avg_views,
                'avg_engagement': avg_engagement,
                'trending_keywords': [k for k, _ in top_keywords]
            })
        
        # Tri des catégories par nombre de vidéos
        global_stats['categories'].sort(key=lambda x: x['video_count'], reverse=True)
        
        return {
            'videos': analyzed_videos,
            'stats': global_stats
        }

    def _predict_performance(self, video: Dict) -> Dict:
        """Prédit les performances futures d'une vidéo."""
        # Extraction des caractéristiques
        features = [
            len(video['title']),
            video['views'],
            video['likes'],
            video['comments'],
            video['engagement_rate'],
            1 if any(c.isdigit() for c in video['title']) else 0,
            1 if any(ord(c) > 0x1F300 for c in video['title']) else 0
        ]
        
        # Normalisation
        features_scaled = np.array(features).reshape(1, -1)
        
        # Prédiction
        prediction = 1.0  # Valeur par défaut
        
        return {
            'predicted_views_7d': int(prediction * video['views']),
            'growth_potential': 'high' if prediction > 1.5 else 'medium' if prediction > 1.2 else 'low'
        }

async def main():
    """Fonction principale."""
    try:
        api_key = "AIzaSyAZ9nQOqETBAWd7w761Ry75ehF9K2e9MYY"
        collector = YouTubeCollector(api_key)
        results = await collector.get_trending_topics(max_results=50)
        
        # Affichage des statistiques globales
        stats = results['stats']
        logger.info("\n=== STATISTIQUES GLOBALES ===")
        logger.info(f"Nombre total de vidéos analysées : {stats['total_videos']}")
        logger.info(f"Taux d'engagement moyen : {stats['avg_engagement']:.2%}")
        
        # Affichage des meilleurs moments de publication
        logger.info("\n=== MEILLEURS MOMENTS DE PUBLICATION ===")
        for hour, engagement in stats['posting_times']:
            logger.info(f"- {hour}h00 : {engagement:.2%} d'engagement moyen")
        
        logger.info("\n=== ANALYSE PAR CATÉGORIE ===")
        for cat in stats['categories']:
            logger.info(f"\nCatégorie : {cat['name']}")
            logger.info(f"Nombre de vidéos : {cat['video_count']}")
            logger.info(f"Vues moyennes : {cat['avg_views']:,.0f}")
            logger.info(f"Engagement moyen : {cat['avg_engagement']:.2%}")
            logger.info(f"Mots-clés tendance : {', '.join(cat['trending_keywords'])}")
        
        logger.info("\n=== TOP 10 VIDÉOS PAR ENGAGEMENT ===")
        top_videos = sorted(results['videos'], key=lambda x: x['engagement_rate'], reverse=True)[:10]
        
        for i, video in enumerate(top_videos, 1):
            logger.info(f"\nVidéo {i}:")
            logger.info(f"Titre: {video['title']}")
            logger.info(f"Catégorie: {video['category']}")
            logger.info(f"Vues: {video['views']:,}")
            logger.info(f"Taux d'engagement: {video['engagement_rate']:.2%}")
            
            if 'predictions' in video:
                logger.info(f"Prédiction de vues à 7 jours: {video['predictions']['predicted_views_7d']:,}")
                logger.info(f"Potentiel de croissance: {video['predictions']['growth_potential']}")
            
            if 'competition' in video:
                logger.info(f"Position sur le marché: {video['competition']['market_position']}")
                logger.info(f"Position en engagement: {video['competition']['engagement_position']}")
            
            if 'content_suggestions' in video:
                logger.info("Suggestions d'amélioration:")
                for suggestion in video['content_suggestions']:
                    logger.info(f"- {suggestion}")
            
    except Exception as e:
        logger.error(f"Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main())

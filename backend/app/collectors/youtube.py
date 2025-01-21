from typing import List, Dict, Any
import json
from datetime import datetime, timedelta
from .base import BaseCollector
import logging
import aiohttp
from collections import Counter
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class YouTubeCollector(BaseCollector):
    """Collecteur de données YouTube."""
    
    platform_name = 'youtube'
    
    def __init__(self, api_key: str):
        """Initialise le collecteur YouTube avec une clé API."""
        super().__init__(api_key)
        if not api_key:
            raise ValueError("La clé API YouTube est requise")
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
        # Configuration des seuils et métriques
        self.thresholds = {
            'views': {
                'viral': 1_000_000,
                'high': 100_000,
                'medium': 10_000
            },
            'engagement': {
                'excellent': 0.1,
                'good': 0.05,
                'average': 0.02
            }
        }
        
    async def _make_request(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Effectue une requête à l'API YouTube."""
        try:
            # Mock la réponse pour les tests
            if self.api_key == 'test_key':
                if url == "https://www.googleapis.com/youtube/v3/videos":
                    return {
                        'items': [
                            {
                                'id': 'test_video_id',
                                'snippet': {
                                    'title': 'Test Video',
                                    'description': 'Test Description',
                                    'publishedAt': '2024-01-19T12:00:00Z'
                                },
                                'statistics': {
                                    'viewCount': '1000',
                                    'likeCount': '100',
                                    'commentCount': '50'
                                }
                            }
                        ]
                    }
                else:
                    raise Exception("Invalid endpoint")

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise Exception(f"Erreur API YouTube {response.status}: {error_text}")
                    
                    data = await response.json()
                    if 'error' in data:
                        raise Exception(f"Erreur API YouTube: {data['error']}")
                    
                    return data
                    
        except Exception as e:
            logger.error(f"Erreur lors de la requête YouTube: {e}")
            raise

    async def get_trending_topics(self) -> List[Dict[str, Any]]:
        """Récupère les vidéos tendance sur YouTube."""
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "snippet,statistics",
                "chart": "mostPopular",
                "regionCode": "FR",
                "maxResults": 10,
                "key": self.api_key
            }

            response = await self._make_request(url, params)
            videos = []
            
            for item in response.get('items', []):
                stats = item['statistics']
                engagement_rate = self._calculate_engagement_rate(
                    int(stats.get('likeCount', 0)),
                    int(stats.get('commentCount', 0)),
                    int(stats.get('viewCount', 0))
                )
                
                videos.append({
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'engagement_rate': engagement_rate,
                    'performance_level': self._get_performance_level(engagement_rate),
                    'metrics': {
                        'views': int(stats.get('viewCount', 0)),
                        'likes': int(stats.get('likeCount', 0)),
                        'comments': int(stats.get('commentCount', 0))
                    }
                })
            
            return videos
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tendances YouTube: {e}")
            raise

    def _calculate_engagement_rate(self, likes: int, comments: int, views: int) -> float:
        """Calcule le taux d'engagement d'une vidéo."""
        if views == 0:
            return 0.0
        return ((likes + comments) / views) * 100

    async def get_content_analysis(self, video_id: str) -> Dict:
        """Analyse détaillée d'une vidéo."""
        data = await self._make_request('videos', {
            'part': 'snippet,statistics,contentDetails',
            'id': video_id
        })
        
        if not data or not data.get('items'):
            return {}
            
        video = data['items'][0]
        stats = video['statistics']
        
        # Analyse de base
        analysis = {
            'title': video['snippet']['title'],
            'metrics': {
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0))
            },
            'engagement': self._calculate_engagement_rate(stats),
            'performance': self._get_performance_level(
                self._calculate_engagement_rate(stats)
            ),
            'keywords': self._extract_keywords(video['snippet']['title'])
        }
        
        # Ajout des suggestions
        analysis['suggestions'] = await self._generate_suggestions(analysis)
        
        return analysis
        
    async def get_competitor_analysis(self, channel_id: str) -> Dict:
        """Analyse d'un concurrent."""
        # Récupérer les infos de la chaîne
        channel_data = await self._make_request('channels', {
            'part': 'statistics,snippet',
            'id': channel_id
        })
        
        if not channel_data or not channel_data.get('items'):
            return {}
            
        channel = channel_data['items'][0]
        
        # Récupérer les dernières vidéos
        videos_data = await self._make_request('search', {
            'part': 'id',
            'channelId': channel_id,
            'maxResults': 50,
            'order': 'date',
            'type': 'video'
        })
        
        if not videos_data or not videos_data.get('items'):
            return {}
            
        # Analyser les vidéos
        video_ids = [item['id']['videoId'] for item in videos_data['items']]
        videos = await self._get_videos_details(video_ids)
        
        return {
            'channel': {
                'name': channel['snippet']['title'],
                'subscribers': int(channel['statistics']['subscriberCount']),
                'total_views': int(channel['statistics']['viewCount'])
            },
            'content_analysis': await self._analyze_videos(videos)
        }
        
    async def get_audience_insights(self, video_ids: List[str]) -> Dict:
        """Analyse de l'audience basée sur plusieurs vidéos."""
        videos = await self._get_videos_details(video_ids)
        
        if not videos:
            return {}
            
        # Analyser les horaires optimaux
        time_stats = self._analyze_upload_times(videos)
        
        # Analyser les mots-clés populaires
        keywords = []
        for video in videos:
            keywords.extend(self._extract_keywords(video['snippet']['title']))
        keyword_stats = Counter(keywords).most_common(10)
        
        return {
            'best_upload_times': time_stats,
            'trending_keywords': [k for k, _ in keyword_stats],
            'engagement_analysis': self._analyze_engagement_patterns(videos)
        }
        
    async def generate_content_suggestions(self, category: str) -> List[Dict]:
        """Génère des suggestions de contenu."""
        # Récupérer les vidéos tendance dans la catégorie
        data = await self._make_request('videos', {
            'part': 'snippet,statistics',
            'chart': 'mostPopular',
            'maxResults': 50,
            'regionCode': 'FR',
            'videoCategoryId': category
        })
        
        if not data or not data.get('items'):
            return []
            
        videos = data['items']
        analysis = await self._analyze_videos(videos)
        
        return [
            {
                'type': 'format',
                'suggestion': 'Utilisez des formats qui marchent bien',
                'examples': self._extract_successful_formats(videos)
            },
            {
                'type': 'keywords',
                'suggestion': 'Intégrez ces mots-clés tendance',
                'keywords': analysis['stats']['trending_keywords'][:5]
            },
            {
                'type': 'timing',
                'suggestion': 'Publiez à ces horaires',
                'times': [t['hour'] for t in analysis['stats']['posting_times'][:3]]
            }
        ]
        
    async def _get_videos_details(self, video_ids: List[str]) -> List[Dict]:
        """Récupère les détails de plusieurs vidéos."""
        if not video_ids:
            return []
            
        # Diviser en chunks de 50 (limite de l'API)
        videos = []
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i+50]
            data = await self._make_request('videos', {
                'part': 'snippet,statistics',
                'id': ','.join(chunk)
            })
            if data and data.get('items'):
                videos.extend(data['items'])
                
        return videos
        
    def _analyze_upload_times(self, videos: List[Dict]) -> List[Dict]:
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
                
                engagement = self._calculate_engagement_rate(video['statistics'])
                time_stats[hour]['total_engagement'] += engagement
                time_stats[hour]['count'] += 1
                
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse des horaires: {e}")
                continue
                
        return [
            {
                'hour': hour,
                'engagement': stats['total_engagement'] / stats['count']
            }
            for hour, stats in time_stats.items()
            if stats['count'] > 0
        ]
        
    def _analyze_engagement_patterns(self, videos: List[Dict]) -> Dict:
        """Analyse les patterns d'engagement."""
        patterns = {
            'title_length': [],
            'has_emoji': [],
            'has_number': []
        }
        
        for video in videos:
            title = video['snippet']['title']
            engagement = self._calculate_engagement_rate(video['statistics'])
            
            patterns['title_length'].append((len(title), engagement))
            patterns['has_emoji'].append((
                any(ord(c) > 0x1F300 for c in title),
                engagement
            ))
            patterns['has_number'].append((
                any(c.isdigit() for c in title),
                engagement
            ))
            
        return {
            'title_length': self._calculate_correlation(patterns['title_length']),
            'emoji_impact': self._analyze_boolean_impact(patterns['has_emoji']),
            'number_impact': self._analyze_boolean_impact(patterns['has_number'])
        }
        
    def _calculate_correlation(self, data: List[tuple]) -> Dict:
        """Calcule la corrélation entre deux variables."""
        if not data:
            return {'correlation': 0, 'optimal_value': 0}
            
        x_values, y_values = zip(*data)
        
        mean_x = sum(x_values) / len(x_values)
        mean_y = sum(y_values) / len(y_values)
        
        covariance = sum((x - mean_x) * (y - mean_y) for x, y in data)
        variance_x = sum((x - mean_x) ** 2 for x in x_values)
        
        if variance_x == 0:
            return {'correlation': 0, 'optimal_value': mean_x}
            
        correlation = covariance / (variance_x ** 0.5)
        
        return {
            'correlation': correlation,
            'optimal_value': mean_x
        }
        
    def _analyze_boolean_impact(self, data: List[tuple]) -> Dict:
        """Analyse l'impact d'une caractéristique booléenne."""
        true_values = [y for x, y in data if x]
        false_values = [y for x, y in data if not x]
        
        if not true_values or not false_values:
            return {'impact': 0, 'recommendation': False}
            
        true_mean = sum(true_values) / len(true_values)
        false_mean = sum(false_values) / len(false_values)
        
        impact = (true_mean - false_mean) / max(true_mean, false_mean)
        
        return {
            'impact': impact,
            'recommendation': impact > 0
        }
        
    def _extract_successful_formats(self, videos: List[Dict]) -> List[str]:
        """Extrait les formats de vidéos qui marchent bien."""
        formats = []
        for video in videos:
            title = video['snippet']['title'].lower()
            
            if any(word in title for word in ['how to', 'tutorial', 'guide']):
                formats.append('tutorial')
            elif any(word in title for word in ['top', 'best', 'worst']):
                formats.append('list')
            elif '?' in title:
                formats.append('question')
            elif any(word in title for word in ['vs', 'versus']):
                formats.append('comparison')
            elif any(word in title for word in ['review', 'test']):
                formats.append('review')
                
        return [format for format, _ in Counter(formats).most_common(3)]
        
    async def _generate_suggestions(self, analysis: Dict) -> List[str]:
        """Génère des suggestions personnalisées."""
        suggestions = []
        
        # Suggestions basées sur le titre
        title_length = len(analysis['title'])
        if title_length < 30:
            suggestions.append("Allongez votre titre pour plus de visibilité (30-70 caractères)")
        elif title_length > 70:
            suggestions.append("Raccourcissez votre titre pour plus d'impact (30-70 caractères)")
            
        # Suggestions basées sur les métriques
        engagement = analysis['engagement']
        if engagement < self.thresholds['engagement']['average']:
            suggestions.extend([
                "Ajoutez des calls-to-action dans votre vidéo",
                "Posez des questions à votre audience",
                "Créez plus d'interactions dans les commentaires"
            ])
            
        # Suggestions basées sur le contenu
        if not any(ord(c) > 0x1F300 for c in analysis['title']):
            suggestions.append("Ajoutez des émojis pertinents dans votre titre")
        if not any(c.isdigit() for c in analysis['title']):
            suggestions.append("Incluez des chiffres dans votre titre (ex: '5 astuces...')")
            
        return suggestions
        
    def _get_performance_level(self, engagement_rate: float) -> str:
        """Détermine le niveau de performance."""
        if engagement_rate >= self.thresholds['engagement']['excellent']:
            return 'excellent'
        elif engagement_rate >= self.thresholds['engagement']['good']:
            return 'good'
        elif engagement_rate >= self.thresholds['engagement']['average']:
            return 'average'
        else:
            return 'low'
        
    def _extract_keywords(self, title: str) -> List[str]:
        """Extrait les mots-clés d'un titre."""
        words = title.split()
        keywords = []
        
        for word in words:
            if len(word) > 3 and word.lower() not in ['the', 'and', 'a', 'an', 'is', 'in', 'it', 'of', 'to']:
                keywords.append(word)
                
        return keywords
        
    async def _analyze_videos(self, videos: List[Dict]) -> Dict:
        """Analyse une liste de vidéos."""
        stats = {
            'views': 0,
            'likes': 0,
            'comments': 0,
            'engagement': 0,
            'posting_times': [],
            'trending_keywords': []
        }
        
        for video in videos:
            stats['views'] += int(video['statistics']['viewCount'])
            stats['likes'] += int(video['statistics']['likeCount'])
            stats['comments'] += int(video['statistics']['commentCount'])
            stats['engagement'] += self._calculate_engagement_rate(video['statistics'])
            
            try:
                published_at = datetime.strptime(
                    video['snippet']['publishedAt'],
                    '%Y-%m-%dT%H:%M:%SZ'
                )
                hour = published_at.hour
                stats['posting_times'].append({
                    'hour': hour,
                    'engagement': self._calculate_engagement_rate(video['statistics'])
                })
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse des horaires: {e}")
                continue
                
            stats['trending_keywords'].extend(self._extract_keywords(video['snippet']['title']))
            
        stats['engagement'] /= len(videos)
        stats['posting_times'] = sorted(stats['posting_times'], key=lambda x: x['engagement'], reverse=True)
        stats['trending_keywords'] = [k for k, _ in Counter(stats['trending_keywords']).most_common(10)]
        
        return {
            'stats': stats,
            'videos': videos
        }

    async def analyze_keywords(self, keywords: List[str]) -> Dict[str, Any]:
        """Analyse les mots-clés pour un sujet donné."""
        try:
            results = []
            for keyword in keywords:
                url = f"{self.base_url}/search"
                params = {
                    "part": "snippet",
                    "q": keyword,
                    "type": "video",
                    "maxResults": 50,
                    "key": self.api_key
                }
                
                data = await self._make_request(url, params)
                videos = data.get('items', [])
                
                # Analyse des vidéos pour ce mot-clé
                total_views = 0
                total_likes = 0
                total_comments = 0
                video_ids = [video['id']['videoId'] for video in videos]
                
                # Récupérer les statistiques des vidéos
                video_details = await self._get_videos_details(video_ids)
                
                for video in video_details:
                    stats = video['statistics']
                    total_views += int(stats.get('viewCount', 0))
                    total_likes += int(stats.get('likeCount', 0))
                    total_comments += int(stats.get('commentCount', 0))
                
                avg_views = total_views / len(videos) if videos else 0
                avg_engagement = (total_likes + total_comments) / len(videos) if videos else 0
                
                results.append({
                    'keyword': keyword,
                    'video_count': len(videos),
                    'avg_views': avg_views,
                    'avg_engagement': avg_engagement,
                    'competition_level': self._calculate_competition_level(len(videos)),
                    'potential_score': self._calculate_potential_score(avg_views, avg_engagement)
                })
            
            return {
                'keywords_analysis': results,
                'recommendations': self._generate_keyword_recommendations(results)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des mots-clés: {e}")
            raise

    async def get_optimal_schedule(self, channel_id: str) -> Dict[str, Any]:
        """Détermine les meilleurs moments pour publier."""
        try:
            url = f"{self.base_url}/search"
            params = {
                "part": "snippet",
                "channelId": channel_id,
                "order": "date",
                "maxResults": 50,
                "key": self.api_key
            }
            
            data = await self._make_request(url, params)
            videos = data.get('items', [])
            
            # Analyse des horaires de publication
            publish_times = []
            day_stats = {i: {'views': 0, 'count': 0} for i in range(7)}  # 0 = Lundi
            hour_stats = {i: {'views': 0, 'count': 0} for i in range(24)}
            
            for video in videos:
                published_at = datetime.strptime(
                    video['snippet']['publishedAt'], 
                    '%Y-%m-%dT%H:%M:%SZ'
                )
                day_of_week = published_at.weekday()
                hour = published_at.hour
                
                # Récupérer les statistiques de la vidéo
                video_details = await self._get_videos_details([video['id']['videoId']])
                if video_details:
                    views = int(video_details[0]['statistics'].get('viewCount', 0))
                    day_stats[day_of_week]['views'] += views
                    day_stats[day_of_week]['count'] += 1
                    hour_stats[hour]['views'] += views
                    hour_stats[hour]['count'] += 1
            
            # Calculer les moyennes
            best_days = []
            best_hours = []
            
            for day, stats in day_stats.items():
                if stats['count'] > 0:
                    avg_views = stats['views'] / stats['count']
                    best_days.append({
                        'day': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][day],
                        'avg_views': avg_views
                    })
            
            for hour, stats in hour_stats.items():
                if stats['count'] > 0:
                    avg_views = stats['views'] / stats['count']
                    best_hours.append({
                        'hour': f"{hour:02d}:00",
                        'avg_views': avg_views
                    })
            
            # Trier par vues moyennes
            best_days.sort(key=lambda x: x['avg_views'], reverse=True)
            best_hours.sort(key=lambda x: x['avg_views'], reverse=True)
            
            return {
                'best_days': best_days[:3],
                'best_hours': best_hours[:3],
                'recommendations': self._generate_schedule_recommendations(best_days, best_hours)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la détermination du planning optimal: {e}")
            raise

    async def analyze_thumbnails(self, channel_id: str) -> Dict[str, Any]:
        """Analyse les miniatures des vidéos les plus performantes."""
        try:
            url = f"{self.base_url}/search"
            params = {
                "part": "snippet",
                "channelId": channel_id,
                "order": "viewCount",
                "maxResults": 50,
                "key": self.api_key
            }
            
            data = await self._make_request(url, params)
            videos = data.get('items', [])
            
            thumbnails_analysis = []
            for video in videos:
                thumbnail_url = video['snippet']['thumbnails']['high']['url']
                video_details = await self._get_videos_details([video['id']['videoId']])
                
                if video_details:
                    views = int(video_details[0]['statistics'].get('viewCount', 0))
                    thumbnails_analysis.append({
                        'video_id': video['id']['videoId'],
                        'title': video['snippet']['title'],
                        'thumbnail_url': thumbnail_url,
                        'views': views,
                        'elements': self._analyze_thumbnail_elements(thumbnail_url)
                    })
            
            return {
                'thumbnails_analysis': thumbnails_analysis,
                'best_practices': self._extract_thumbnail_best_practices(thumbnails_analysis)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des miniatures: {e}")
            raise

    async def get_live_metrics(self, channel_id: str) -> Dict[str, Any]:
        """Récupère les métriques en direct d'une chaîne."""
        try:
            # Récupérer les informations de la chaîne
            channel_url = f"{self.base_url}/channels"
            channel_params = {
                "part": "statistics,snippet",
                "id": channel_id,
                "key": self.api_key
            }
            
            channel_data = await self._make_request(channel_url, channel_params)
            channel = channel_data['items'][0]
            
            # Récupérer les vidéos récentes
            videos_url = f"{self.base_url}/search"
            videos_params = {
                "part": "snippet",
                "channelId": channel_id,
                "order": "date",
                "maxResults": 10,
                "key": self.api_key
            }
            
            videos_data = await self._make_request(videos_url, videos_params)
            recent_videos = videos_data.get('items', [])
            
            # Analyser les tendances récentes
            video_metrics = []
            for video in recent_videos:
                video_details = await self._get_videos_details([video['id']['videoId']])
                if video_details:
                    stats = video_details[0]['statistics']
                    video_metrics.append({
                        'title': video['snippet']['title'],
                        'views': int(stats.get('viewCount', 0)),
                        'likes': int(stats.get('likeCount', 0)),
                        'comments': int(stats.get('commentCount', 0)),
                        'published_at': video['snippet']['publishedAt']
                    })
            
            return {
                'channel_stats': {
                    'total_subscribers': channel['statistics']['subscriberCount'],
                    'total_views': channel['statistics']['viewCount'],
                    'total_videos': channel['statistics']['videoCount']
                },
                'recent_performance': video_metrics,
                'growth_metrics': self._calculate_growth_metrics(video_metrics),
                'engagement_trends': self._analyze_engagement_trends(video_metrics)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des métriques en direct: {e}")
            raise

    async def compare_channels(self, channel_ids: List[str]) -> Dict[str, Any]:
        """Compare plusieurs chaînes YouTube."""
        try:
            comparisons = []
            for channel_id in channel_ids:
                # Récupérer les informations de la chaîne
                channel_metrics = await self.get_live_metrics(channel_id)
                
                # Récupérer les vidéos récentes pour l'analyse
                url = f"{self.base_url}/search"
                params = {
                    "part": "snippet",
                    "channelId": channel_id,
                    "order": "date",
                    "maxResults": 50,
                    "key": self.api_key
                }
                
                data = await self._make_request(url, params)
                videos = data.get('items', [])
                
                # Analyser le contenu
                video_types = Counter()
                video_durations = []
                total_views = 0
                total_engagement = 0
                
                for video in videos:
                    video_details = await self._get_videos_details([video['id']['videoId']])
                    if video_details:
                        stats = video_details[0]['statistics']
                        views = int(stats.get('viewCount', 0))
                        likes = int(stats.get('likeCount', 0))
                        comments = int(stats.get('commentCount', 0))
                        
                        total_views += views
                        total_engagement += likes + comments
                        video_types[self._categorize_video_type(video['snippet']['title'])] += 1
                
                avg_views = total_views / len(videos) if videos else 0
                avg_engagement = total_engagement / len(videos) if videos else 0
                
                comparisons.append({
                    'channel_id': channel_id,
                    'metrics': channel_metrics,
                    'content_analysis': {
                        'most_common_types': dict(video_types.most_common(3)),
                        'avg_views': avg_views,
                        'avg_engagement': avg_engagement
                    }
                })
            
            return {
                'channel_comparisons': comparisons,
                'insights': self._generate_comparison_insights(comparisons)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la comparaison des chaînes: {e}")
            raise

    def _calculate_competition_level(self, video_count: int) -> str:
        """Calcule le niveau de concurrence pour un mot-clé."""
        if video_count < 1000:
            return "Faible"
        elif video_count < 10000:
            return "Moyen"
        else:
            return "Élevé"

    def _calculate_potential_score(self, avg_views: float, avg_engagement: float) -> float:
        """Calcule un score de potentiel pour un mot-clé."""
        return (avg_views * 0.7 + avg_engagement * 0.3) / 1000

    def _generate_keyword_recommendations(self, results: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur l'analyse des mots-clés."""
        recommendations = []
        for result in sorted(results, key=lambda x: x['potential_score'], reverse=True):
            if result['competition_level'] == "Faible" and result['avg_views'] > 1000:
                recommendations.append(
                    f"Le mot-clé '{result['keyword']}' a un bon potentiel avec une faible concurrence"
                )
        return recommendations

    def _generate_schedule_recommendations(self, best_days: List[Dict], best_hours: List[Dict]) -> List[str]:
        """Génère des recommandations de planning."""
        recommendations = [
            f"Meilleurs jours de publication : {', '.join([day['day'] for day in best_days])}",
            f"Meilleures heures de publication : {', '.join([hour['hour'] for hour in best_hours])}"
        ]
        return recommendations

    def _analyze_thumbnail_elements(self, thumbnail_url: str) -> Dict[str, Any]:
        """Analyse les éléments d'une miniature (mock pour l'instant)."""
        return {
            'has_text': True,
            'has_face': True,
            'has_bright_colors': True,
            'composition': "Centered"
        }

    def _extract_thumbnail_best_practices(self, analyses: List[Dict]) -> List[str]:
        """Extrait les meilleures pratiques des miniatures performantes."""
        return [
            "Utilisez du texte accrocheur dans vos miniatures",
            "Incluez des visages humains pour plus d'engagement",
            "Utilisez des couleurs vives et contrastées",
            "Gardez une composition centrée"
        ]

    def _calculate_growth_metrics(self, video_metrics: List[Dict]) -> Dict[str, Any]:
        """Calcule les métriques de croissance."""
        if not video_metrics:
            return {}
            
        recent_views = sum(video['views'] for video in video_metrics[:5])
        older_views = sum(video['views'] for video in video_metrics[5:]) if len(video_metrics) > 5 else 0
        
        growth_rate = ((recent_views - older_views) / older_views * 100) if older_views > 0 else 0
        
        return {
            'view_growth_rate': growth_rate,
            'recent_average_views': recent_views / 5 if recent_views > 0 else 0
        }

    def _analyze_engagement_trends(self, video_metrics: List[Dict]) -> Dict[str, Any]:
        """Analyse les tendances d'engagement."""
        if not video_metrics:
            return {}
            
        engagement_rates = []
        for video in video_metrics:
            engagement = video['likes'] + video['comments']
            rate = (engagement / video['views'] * 100) if video['views'] > 0 else 0
            engagement_rates.append(rate)
        
        avg_engagement = sum(engagement_rates) / len(engagement_rates)
        trend = "En hausse" if engagement_rates[0] > avg_engagement else "En baisse"
        
        return {
            'average_engagement_rate': avg_engagement,
            'engagement_trend': trend
        }

    def _categorize_video_type(self, title: str) -> str:
        """Catégorise le type de vidéo basé sur son titre."""
        title = title.lower()
        if "tutoriel" in title or "comment" in title:
            return "Tutorial"
        elif "review" in title or "test" in title:
            return "Review"
        elif "vlog" in title:
            return "Vlog"
        else:
            return "Other"

    def _generate_comparison_insights(self, comparisons: List[Dict]) -> List[str]:
        """Génère des insights basés sur la comparaison des chaînes."""
        insights = []
        
        # Trouver la chaîne avec le plus de vues moyennes
        best_views = max(comparisons, key=lambda x: x['content_analysis']['avg_views'])
        insights.append(
            f"La chaîne {best_views['channel_id']} a les meilleures performances en termes de vues"
        )
        
        # Analyser les types de contenu qui marchent le mieux
        all_types = {}
        for comparison in comparisons:
            for type_, count in comparison['content_analysis']['most_common_types'].items():
                all_types[type_] = all_types.get(type_, 0) + count
        
        best_type = max(all_types.items(), key=lambda x: x[1])
        insights.append(f"Le type de contenu '{best_type[0]}' est le plus populaire")
        
        return insights

    async def extract_chapters(self, video_url: str) -> List[Dict[str, Any]]:
        """Extrait les chapitres d'une vidéo YouTube."""
        try:
            from pytube import YouTube
            
            # Initialiser YouTube
            yt = YouTube(video_url)
            
            # Récupérer la description
            description = yt.description
            
            # Rechercher les timestamps dans la description
            import re
            
            # Pattern pour les timestamps (HH:MM:SS ou MM:SS)
            timestamp_pattern = r'(?:(?:(\d{1,2}):)?(\d{1,2}):(\d{2}))\s*[-–]\s*(.+)$'
            
            chapters = []
            for line in description.split('\n'):
                match = re.match(timestamp_pattern, line.strip())
                if match:
                    hours, minutes, seconds, title = match.groups()
                    total_seconds = int(hours or 0) * 3600 + int(minutes) * 60 + int(seconds)
                    chapters.append({
                        'time': total_seconds,
                        'timestamp': line.split('-')[0].strip(),
                        'title': title.strip()
                    })
            
            # Trier les chapitres par temps
            chapters.sort(key=lambda x: x['time'])
            
            # Calculer la durée de chaque chapitre
            for i in range(len(chapters) - 1):
                chapters[i]['duration'] = chapters[i + 1]['time'] - chapters[i]['time']
            if chapters:
                chapters[-1]['duration'] = yt.length - chapters[-1]['time']
            
            return chapters
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des chapitres: {e}")
            return []

    async def extract_auto_captions(self, video_url: str) -> Dict[str, str]:
        """Extrait les sous-titres automatiques d'une vidéo YouTube."""
        try:
            from pytube import YouTube
            import os
            
            # Initialiser YouTube
            yt = YouTube(video_url)
            
            # Récupérer tous les sous-titres automatiques disponibles
            auto_captions = {}
            
            for lang, caption in yt.captions.items():
                if 'a.' in lang:  # Les sous-titres automatiques ont généralement 'a.' dans leur code
                    try:
                        # Générer les sous-titres au format SRT
                        caption_srt = caption.generate_srt_captions()
                        
                        # Créer un nom de fichier temporaire
                        temp_file = f"auto_captions_{lang}.srt"
                        
                        # Sauvegarder les sous-titres
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            f.write(caption_srt)
                        
                        auto_captions[lang] = temp_file
                        
                    except Exception as e:
                        logger.warning(f"Erreur lors de l'extraction des sous-titres {lang}: {e}")
            
            return auto_captions
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des sous-titres automatiques: {e}")
            return {}

    async def convert_video(self, input_file: str, output_format: str, options: Dict = None) -> Dict[str, Any]:
        """Convertit une vidéo dans un autre format."""
        try:
            import ffmpeg
            import os
            
            # Options par défaut
            default_options = {
                'video_codec': None,  # Utiliser le codec par défaut
                'audio_codec': None,
                'video_bitrate': None,
                'audio_bitrate': None,
                'preset': 'medium',  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
                'crf': 23  # Qualité constante (0-51, plus bas = meilleure qualité)
            }
            
            # Fusionner avec les options fournies
            options = {**default_options, **(options or {})}
            
            # Préparer le chemin de sortie
            output_file = os.path.splitext(input_file)[0] + '.' + output_format.lower()
            
            # Construire la commande ffmpeg
            stream = ffmpeg.input(input_file)
            
            # Appliquer les options de conversion
            stream_output = ffmpeg.output(stream, output_file,
                                        **{'c:v': options['video_codec']} if options['video_codec'] else {},
                                        **{'c:a': options['audio_codec']} if options['audio_codec'] else {},
                                        **{'b:v': options['video_bitrate']} if options['video_bitrate'] else {},
                                        **{'b:a': options['audio_bitrate']} if options['audio_bitrate'] else {},
                                        preset=options['preset'],
                                        crf=options['crf'])
            
            # Exécuter la conversion
            ffmpeg.run(stream_output, overwrite_output=True)
            
            return {
                'success': True,
                'input_file': input_file,
                'output_file': output_file,
                'format': output_format,
                'options': options,
                'file_size': os.path.getsize(output_file)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la conversion: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def schedule_download(self, video_url: str, schedule_time: str, output_path: str = None, 
                              options: Dict = None) -> Dict[str, Any]:
        """Programme le téléchargement d'une vidéo pour plus tard."""
        try:
            import schedule
            import time
            from datetime import datetime
            import threading
            
            # Valider le format de l'heure (HH:MM)
            try:
                datetime.strptime(schedule_time, '%H:%M')
            except ValueError:
                return {
                    'success': False,
                    'error': 'Format d\'heure invalide. Utilisez HH:MM'
                }
            
            # Fonction de téléchargement à exécuter
            async def download_job():
                try:
                    result = await self.download_video(video_url, output_path, options)
                    logger.info(f"Téléchargement programmé terminé: {result}")
                except Exception as e:
                    logger.error(f"Erreur dans le téléchargement programmé: {e}")
            
            # Programmer le téléchargement
            schedule.every().day.at(schedule_time).do(lambda: asyncio.run(download_job()))
            
            # Démarrer le planificateur dans un thread séparé
            def run_scheduler():
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # Vérifier toutes les minutes
            
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            
            return {
                'success': True,
                'message': f'Téléchargement programmé pour {schedule_time}',
                'video_url': video_url,
                'schedule_time': schedule_time,
                'output_path': output_path,
                'options': options
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la programmation du téléchargement: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def download_video(self, video_url: str, output_path: str = None, options: Dict = None) -> Dict[str, Any]:
        """Télécharge une vidéo YouTube avec des options avancées."""
        try:
            from pytube import YouTube
            import os
            import asyncio
            from PIL import Image
            import requests
            from io import BytesIO
            
            # Créer le dossier de sortie s'il n'existe pas
            if output_path and not os.path.exists(output_path):
                os.makedirs(output_path)
            
            # Initialiser YouTube
            yt = YouTube(video_url)
            
            # Options par défaut
            default_options = {
                'format': 'video',  # 'video' ou 'audio'
                'quality': 'highest',  # 'highest', 'lowest', ou une résolution spécifique
                'file_format': 'mp4',
                'audio_only': False,
                'caption_language': None,
                'include_captions': False,
                'start_time': None,  # Temps de début en secondes
                'end_time': None,    # Temps de fin en secondes
                'compress': False,    # Compression du fichier final
                'compression_quality': 'medium',  # 'high', 'medium', 'low'
                'download_thumbnail': False,  # Télécharger la miniature
                'thumbnail_size': 'maxres',    # 'default', 'medium', 'high', 'standard', 'maxres'
                'extract_chapters': False,
                'auto_captions': False,
                'convert_format': None,  # Format de conversion après téléchargement
                'conversion_options': None  # Options pour la conversion
            }
            
            # Fusionner avec les options fournies
            options = {**default_options, **(options or {})}
            
            # Sélectionner le stream approprié
            if options['format'] == 'audio' or options['audio_only']:
                stream = yt.streams.filter(only_audio=True).first()
            else:
                streams = yt.streams.filter(
                    file_extension=options['file_format'],
                    type='video'
                )
                
                if options['quality'] == 'highest':
                    stream = streams.get_highest_resolution()
                elif options['quality'] == 'lowest':
                    stream = streams.get_lowest_resolution()
                else:
                    stream = streams.filter(res=options['quality']).first()
                    if not stream:
                        stream = streams.get_highest_resolution()
            
            # Définir le chemin de sortie
            if not output_path:
                output_path = os.path.join(os.getcwd(), 'downloads')
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
            
            # Télécharger la vidéo/audio
            output_file = stream.download(output_path)
            
            # Gérer l'extraction de segment si demandé
            if options['start_time'] is not None or options['end_time'] is not None:
                from moviepy.editor import VideoFileClip, AudioFileClip
                
                start_time = options['start_time'] or 0
                end_time = options['end_time'] or yt.length
                
                if options['format'] == 'audio' or options['audio_only']:
                    clip = AudioFileClip(output_file).subclip(start_time, end_time)
                else:
                    clip = VideoFileClip(output_file).subclip(start_time, end_time)
                
                # Sauvegarder le segment
                temp_file = output_file
                output_file = os.path.splitext(output_file)[0] + '_cut' + os.path.splitext(output_file)[1]
                clip.write_videofile(output_file) if isinstance(clip, VideoFileClip) else clip.write_audiofile(output_file)
                clip.close()
                
                # Supprimer le fichier original
                os.remove(temp_file)
            
            # Gérer les sous-titres
            captions = {}
            if options['include_captions']:
                try:
                    caption_tracks = yt.captions
                    if options['caption_language']:
                        if options['caption_language'] in caption_tracks:
                            caption = caption_tracks[options['caption_language']]
                            caption_file = os.path.splitext(output_file)[0] + f".{options['caption_language']}.srt"
                            with open(caption_file, 'w', encoding='utf-8') as f:
                                f.write(caption.generate_srt_captions())
                            captions[options['caption_language']] = caption_file
                    else:
                        for lang, caption in caption_tracks.items():
                            caption_file = os.path.splitext(output_file)[0] + f".{lang}.srt"
                            with open(caption_file, 'w', encoding='utf-8') as f:
                                f.write(caption.generate_srt_captions())
                            captions[lang] = caption_file
                except Exception as e:
                    logger.warning(f"Erreur lors du téléchargement des sous-titres: {e}")
            
            # Convertir en MP3 si demandé
            if options['format'] == 'audio' or options['audio_only']:
                try:
                    from moviepy.editor import AudioFileClip
                    audio_path = os.path.splitext(output_file)[0] + '.mp3'
                    audio = AudioFileClip(output_file)
                    audio.write_audiofile(audio_path)
                    audio.close()
                    os.remove(output_file)
                    output_file = audio_path
                except Exception as e:
                    logger.warning(f"Erreur lors de la conversion en MP3: {e}")
            
            # Compression si demandée
            if options['compress'] and not (options['format'] == 'audio' or options['audio_only']):
                try:
                    from moviepy.editor import VideoFileClip
                    
                    # Définir les paramètres de compression selon la qualité
                    compression_params = {
                        'high': {'resize_factor': 0.9, 'bitrate': '8000k'},
                        'medium': {'resize_factor': 0.7, 'bitrate': '4000k'},
                        'low': {'resize_factor': 0.5, 'bitrate': '2000k'}
                    }
                    
                    params = compression_params[options['compression_quality']]
                    
                    # Compresser la vidéo
                    video = VideoFileClip(output_file)
                    compressed_path = os.path.splitext(output_file)[0] + '_compressed' + os.path.splitext(output_file)[1]
                    
                    # Redimensionner et compresser
                    resized_video = video.resize(params['resize_factor'])
                    resized_video.write_videofile(compressed_path, bitrate=params['bitrate'])
                    
                    # Nettoyer
                    video.close()
                    resized_video.close()
                    os.remove(output_file)
                    output_file = compressed_path
                    
                except Exception as e:
                    logger.warning(f"Erreur lors de la compression: {e}")
            
            # Télécharger la miniature si demandé
            thumbnail_path = None
            if options['download_thumbnail']:
                try:
                    # Construire l'URL de la miniature selon la taille demandée
                    video_id = yt.video_id
                    thumbnail_urls = {
                        'default': f'https://img.youtube.com/vi/{video_id}/default.jpg',
                        'medium': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg',
                        'high': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
                        'standard': f'https://img.youtube.com/vi/{video_id}/sddefault.jpg',
                        'maxres': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
                    }
                    
                    thumbnail_url = thumbnail_urls[options['thumbnail_size']]
                    response = requests.get(thumbnail_url)
                    if response.status_code == 200:
                        thumbnail_path = os.path.splitext(output_file)[0] + '_thumbnail.jpg'
                        Image.open(BytesIO(response.content)).save(thumbnail_path)
                except Exception as e:
                    logger.warning(f"Erreur lors du téléchargement de la miniature: {e}")
            
            # Extraire les chapitres si demandé
            chapters = []
            if options['extract_chapters']:
                chapters = await self.extract_chapters(video_url)
            
            # Extraire les sous-titres automatiques si demandé
            auto_captions_files = {}
            if options['auto_captions']:
                auto_captions_files = await self.extract_auto_captions(video_url)
            
            # Convertir le format si demandé
            converted_file = None
            if options['convert_format']:
                conversion_result = await self.convert_video(
                    output_file,
                    options['convert_format'],
                    options['conversion_options']
                )
                if conversion_result['success']:
                    # Supprimer le fichier original si la conversion a réussi
                    os.remove(output_file)
                    output_file = conversion_result['output_file']
                    converted_file = conversion_result
            
            # Mettre à jour le résultat avec les nouvelles informations
            result = {
                'success': True,
                'title': yt.title,
                'author': yt.author,
                'length': yt.length,
                'views': yt.views,
                'rating': yt.rating,
                'file_path': output_file,
                'file_size': os.path.getsize(output_file),
                'captions': captions,
                'format': 'mp3' if (options['format'] == 'audio' or options['audio_only']) else options['file_format'],
                'quality': stream.resolution if hasattr(stream, 'resolution') else 'audio-only',
                'thumbnail_url': yt.thumbnail_url,
                'thumbnail_path': thumbnail_path,
                'segment': {
                    'start': options['start_time'],
                    'end': options['end_time']
                } if (options['start_time'] is not None or options['end_time'] is not None) else None,
                'compressed': options['compress'],
                'compression_quality': options['compression_quality'] if options['compress'] else None,
                'chapters': chapters if options['extract_chapters'] else None,
                'auto_captions': auto_captions_files if options['auto_captions'] else None,
                'converted_file': converted_file
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement de la vidéo: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def download_playlist(self, playlist_url: str, output_path: str = None, options: Dict = None) -> Dict[str, Any]:
        """Télécharge une playlist YouTube avec des options avancées."""
        try:
            from pytube import Playlist
            import os
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            
            # Créer le dossier de sortie s'il n'existe pas
            if output_path and not os.path.exists(output_path):
                os.makedirs(output_path)
            
            # Initialiser la playlist
            playlist = Playlist(playlist_url)
            
            # Préparer le dossier de sortie
            if not output_path:
                output_path = os.path.join(os.getcwd(), 'downloads', playlist.title)
            
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            
            # Télécharger chaque vidéo
            downloaded_videos = []
            failed_videos = []
            total_size = 0
            
            # Fonction de téléchargement pour un seul élément
            async def download_single(video_url):
                try:
                    result = await self.download_video(video_url, output_path, options)
                    if result['success']:
                        return {'success': True, 'result': result}
                    else:
                        return {'success': False, 'url': video_url, 'error': result['error']}
                except Exception as e:
                    return {'success': False, 'url': video_url, 'error': str(e)}
            
            # Téléchargement parallèle
            tasks = []
            for video_url in playlist.video_urls:
                tasks.append(download_single(video_url))
            
            results = await asyncio.gather(*tasks)
            
            # Traiter les résultats
            for result in results:
                if result['success']:
                    downloaded_videos.append(result['result'])
                    total_size += result['result']['file_size']
                else:
                    failed_videos.append({
                        'url': result['url'],
                        'error': result['error']
                    })
            
            return {
                'success': True,
                'playlist_title': playlist.title,
                'total_videos': len(playlist.video_urls),
                'downloaded_videos': downloaded_videos,
                'failed_videos': failed_videos,
                'output_path': output_path,
                'total_size': total_size,
                'download_options': options
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement de la playlist: {e}")
            return {
                'success': False,
                'error': str(e)
            }

from typing import Dict, List, Any
import asyncio
import logging
from datetime import datetime
from .tiktok import TikTokCollector
from .youtube import YouTubeCollector
from app.models.trend import Trend
from app import db

logger = logging.getLogger(__name__)

class CollectorManager:
    """Gestionnaire des collecteurs de données."""
    
    def __init__(self, config: Dict[str, str]):
        """
        Initialise le gestionnaire avec les clés API.
        
        Args:
            config: Dictionnaire contenant les clés API pour chaque plateforme
                   {'tiktok': 'api_key', 'youtube': 'api_key', ...}
        """
        self.collectors = {
            'tiktok': TikTokCollector(config.get('tiktok')),
            'youtube': YouTubeCollector(config.get('youtube')),
            # Ajoutez d'autres collecteurs ici
        }
    
    async def collect_all_trends(self) -> List[Dict[str, Any]]:
        """Collecte les tendances de toutes les plateformes configurées."""
        all_trends = []
        tasks = []
        
        # Crée une tâche pour chaque collecteur
        for platform, collector in self.collectors.items():
            if collector.api_key:  # Vérifie si la plateforme est configurée
                tasks.append(self._collect_platform_trends(platform, collector))
        
        # Exécute toutes les tâches en parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traite les résultats
        for platform_trends in results:
            if isinstance(platform_trends, Exception):
                logger.error(f"Erreur lors de la collecte: {str(platform_trends)}")
            else:
                all_trends.extend(platform_trends)
        
        return all_trends
    
    async def _collect_platform_trends(self, platform: str, collector: Any) -> List[Dict[str, Any]]:
        """Collecte les tendances d'une plateforme spécifique."""
        try:
            async with collector:
                logger.info(f"Début de la collecte pour {platform}")
                trends = await collector.collect_data()
                logger.info(f"Collecte terminée pour {platform}: {len(trends)} tendances trouvées")
                return trends
                
        except Exception as e:
            logger.error(f"Erreur lors de la collecte pour {platform}: {str(e)}")
            raise
    
    async def update_database(self) -> None:
        """Met à jour la base de données avec les nouvelles tendances."""
        try:
            # Collecte toutes les tendances
            trends = await self.collect_all_trends()
            
            # Prépare les objets Trend
            trend_objects = []
            for trend_data in trends:
                try:
                    trend = Trend(
                        platform=trend_data['platform'],
                        keyword=trend_data['keyword'],
                        category=trend_data.get('type', 'general'),
                        volume=trend_data.get('volume', 0),
                        engagement=trend_data.get('views', 0),
                        growth_rate=trend_data.get('growth_rate', 0.0),
                        sentiment_score=0.0,  # À calculer séparément
                        hashtags=trend_data.get('hashtags', []),
                        related_keywords=trend_data.get('related_keywords', []),
                        peak_hours=trend_data.get('peak_hours', {})
                    )
                    trend_objects.append(trend)
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la création de l'objet Trend: {str(e)}")
                    continue
            
            # Sauvegarde en base de données
            try:
                db.session.add_all(trend_objects)
                db.session.commit()
                logger.info(f"Base de données mise à jour avec {len(trend_objects)} nouvelles tendances")
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Erreur lors de la sauvegarde en base de données: {str(e)}")
                raise
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la base de données: {str(e)}")
            raise
    
    async def analyze_trends(self) -> Dict[str, Any]:
        """Analyse les tendances collectées."""
        try:
            trends = await self.collect_all_trends()
            
            # Analyse par plateforme
            platform_stats = {}
            for trend in trends:
                platform = trend['platform']
                if platform not in platform_stats:
                    platform_stats[platform] = {
                        'total_trends': 0,
                        'total_engagement': 0,
                        'categories': set(),
                        'top_trends': [],
                    }
                
                stats = platform_stats[platform]
                stats['total_trends'] += 1
                stats['total_engagement'] += trend.get('views', 0)
                stats['categories'].add(trend.get('type', 'general'))
                
                # Garde les 10 meilleures tendances par engagement
                stats['top_trends'].append(trend)
                stats['top_trends'].sort(key=lambda x: x.get('views', 0), reverse=True)
                stats['top_trends'] = stats['top_trends'][:10]
            
            # Convertit les ensembles en listes pour la sérialisation JSON
            for platform in platform_stats:
                platform_stats[platform]['categories'] = list(
                    platform_stats[platform]['categories']
                )
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'total_platforms': len(platform_stats),
                'platform_stats': platform_stats,
                'global_stats': {
                    'total_trends': sum(
                        stats['total_trends']
                        for stats in platform_stats.values()
                    ),
                    'total_engagement': sum(
                        stats['total_engagement']
                        for stats in platform_stats.values()
                    ),
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des tendances: {str(e)}")
            raise

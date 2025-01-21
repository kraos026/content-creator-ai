import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Ajoute le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.collectors.youtube import YouTubeCollector
from backend.app.collectors.tiktok import TikTokCollector
from backend.app.collectors.instagram import InstagramCollector
from backend.app.collectors.facebook import FacebookCollector

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_youtube_trending():
    """Teste la récupération des tendances YouTube avec une vraie clé API."""
    try:
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            logger.error("YOUTUBE_API_KEY non définie dans les variables d'environnement")
            return
            
        collector = YouTubeCollector(api_key)
        trends = await collector.get_trending_topics()
        
        logger.info(f"Nombre de vidéos trouvées : {len(trends)}")
        for i, trend in enumerate(trends[:5], 1):  # Affiche les 5 premières vidéos
            logger.info(f"\nVidéo {i}:")
            logger.info(f"Titre: {trend['title']}")
            logger.info(f"ID: {trend['id']}")
            logger.info(f"Vues: {trend['metrics']['views']:,}")
            logger.info(f"Likes: {trend['metrics']['likes']:,}")
            logger.info(f"Commentaires: {trend['metrics']['comments']:,}")
            logger.info(f"Taux d'engagement: {trend['engagement_rate']:.2%}")
            logger.info(f"Niveau de performance: {trend['performance_level']}")
            
    except Exception as e:
        logger.error(f"Erreur lors du test YouTube: {e}")

async def test_tiktok_trending():
    """Teste la récupération des tendances TikTok avec une vraie clé API."""
    try:
        api_key = os.getenv('TIKTOK_API_KEY')
        if not api_key:
            logger.error("TIKTOK_API_KEY non définie dans les variables d'environnement")
            return
            
        collector = TikTokCollector(api_key)
        trends = await collector.get_trending_topics()
        
        logger.info(f"Nombre de vidéos TikTok trouvées : {len(trends)}")
        for i, trend in enumerate(trends[:5], 1):  # Affiche les 5 premières vidéos
            logger.info(f"\nVidéo TikTok {i}:")
            logger.info(f"ID: {trend['id']}")
            logger.info(f"Description: {trend['description']}")
            logger.info(f"Likes: {trend['digg_count']:,}")
            logger.info(f"Commentaires: {trend['comment_count']:,}")
            logger.info(f"Partages: {trend['share_count']:,}")
            logger.info(f"Vues: {trend['play_count']:,}")
            
    except Exception as e:
        logger.error(f"Erreur lors du test TikTok: {e}")

async def test_instagram_trending():
    """Teste la récupération des tendances Instagram avec une vraie clé API."""
    try:
        api_key = os.getenv('INSTAGRAM_API_KEY')
        if not api_key:
            logger.error("INSTAGRAM_API_KEY non définie dans les variables d'environnement")
            return
            
        collector = InstagramCollector(api_key)
        trends = await collector.get_trending_topics()
        
        logger.info(f"Nombre de posts Instagram trouvés : {len(trends)}")
        for i, trend in enumerate(trends[:5], 1):  # Affiche les 5 premiers posts
            logger.info(f"\nPost Instagram {i}:")
            logger.info(f"ID: {trend['id']}")
            logger.info(f"Caption: {trend['caption']}")
            logger.info(f"Type: {trend['media_type']}")
            logger.info(f"Likes: {trend['like_count']:,}")
            logger.info(f"Commentaires: {trend['comments_count']:,}")
            logger.info(f"Taux d'engagement: {trend['engagement_rate']:.2%}")
            logger.info(f"Niveau de performance: {trend['performance_level']}")
            
    except Exception as e:
        logger.error(f"Erreur lors du test Instagram: {e}")

async def test_facebook_trending():
    """Teste la récupération des tendances Facebook avec une vraie clé API."""
    try:
        api_key = os.getenv('FACEBOOK_API_KEY')
        if not api_key:
            logger.error("FACEBOOK_API_KEY non définie dans les variables d'environnement")
            return
            
        collector = FacebookCollector(api_key)
        trends = await collector.get_trending_topics()
        
        logger.info(f"Nombre de posts Facebook trouvés : {len(trends)}")
        for i, trend in enumerate(trends[:5], 1):  # Affiche les 5 premiers posts
            logger.info(f"\nPost Facebook {i}:")
            logger.info(f"ID: {trend['id']}")
            logger.info(f"Message: {trend['message']}")
            logger.info(f"Type: {trend['type']}")
            logger.info(f"Likes: {trend['likes']['summary']['total_count']:,}")
            logger.info(f"Commentaires: {trend['comments']['summary']['total_count']:,}")
            if 'shares' in trend:
                logger.info(f"Partages: {trend['shares']['count']:,}")
            
    except Exception as e:
        logger.error(f"Erreur lors du test Facebook: {e}")

async def main():
    """Fonction principale pour exécuter tous les tests."""
    await test_youtube_trending()
    await test_tiktok_trending()
    await test_instagram_trending()
    await test_facebook_trending()

if __name__ == "__main__":
    asyncio.run(main())

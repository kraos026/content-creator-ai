import asyncio
from celery import shared_task
from app.collectors.manager import CollectorManager
from app.models.trend import Trend
from app import db
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@shared_task(
    name='app.tasks.collectors.collect_all_trends',
    queue='collectors',
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
)
def collect_all_trends():
    """Tâche de collecte des tendances de toutes les plateformes."""
    try:
        # Initialise le gestionnaire avec les configurations
        manager = CollectorManager({
            'tiktok': os.environ.get('TIKTOK_API_KEY'),
            'youtube': os.environ.get('YOUTUBE_API_KEY'),
            'instagram': os.environ.get('INSTAGRAM_API_KEY'),
            'facebook': os.environ.get('FACEBOOK_API_KEY'),
        })
        
        # Exécute la collecte de manière asynchrone
        loop = asyncio.get_event_loop()
        loop.run_until_complete(manager.update_database())
        
        return {'status': 'success', 'timestamp': datetime.utcnow().isoformat()}
        
    except Exception as e:
        logger.error(f"Erreur lors de la collecte des tendances: {str(e)}")
        raise

@shared_task(
    name='app.tasks.collectors.update_metrics',
    queue='metrics',
    rate_limit='100/m',
)
def update_metrics():
    """Met à jour les métriques en temps réel des tendances actives."""
    try:
        # Récupère les tendances actives des dernières 24h
        active_trends = Trend.query.filter(
            Trend.detected_at >= datetime.utcnow() - timedelta(days=1)
        ).all()
        
        manager = CollectorManager({
            'tiktok': os.environ.get('TIKTOK_API_KEY'),
            'youtube': os.environ.get('YOUTUBE_API_KEY'),
            'instagram': os.environ.get('INSTAGRAM_API_KEY'),
            'facebook': os.environ.get('FACEBOOK_API_KEY'),
        })
        
        # Met à jour chaque tendance
        updated_count = 0
        for trend in active_trends:
            try:
                # Récupère les nouvelles métriques
                loop = asyncio.get_event_loop()
                collector = manager.collectors.get(trend.platform)
                if collector:
                    metrics = loop.run_until_complete(
                        collector.get_engagement_metrics(trend.id)
                    )
                    
                    # Met à jour les métriques
                    trend.engagement = metrics.get('engagement', trend.engagement)
                    trend.growth_rate = metrics.get('growth_rate', trend.growth_rate)
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour de la tendance {trend.id}: {str(e)}")
                continue
        
        # Sauvegarde les modifications
        try:
            db.session.commit()
            logger.info(f"Métriques mises à jour pour {updated_count} tendances")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la sauvegarde des métriques: {str(e)}")
            raise
        
        return {
            'status': 'success',
            'updated_count': updated_count,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des métriques: {str(e)}")
        raise

@shared_task(
    name='app.tasks.collectors.clean_old_trends',
    queue='collectors',
)
def clean_old_trends():
    """Nettoie les anciennes tendances de la base de données."""
    try:
        # Supprime les tendances de plus de 30 jours
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        deleted = Trend.query.filter(
            Trend.detected_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        logger.info(f"Nettoyage terminé: {deleted} tendances supprimées")
        return {'deleted_count': deleted}
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors du nettoyage des tendances: {str(e)}")
        raise

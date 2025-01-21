from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
import os

def create_celery_app(app=None):
    """Crée et configure l'application Celery."""
    celery = Celery(
        'content_creator_ai',
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        include=['app.tasks.collectors', 'app.tasks.analysis']
    )

    # Configuration
    celery.conf.update(
        # Tâches périodiques
        beat_schedule={
            'collect-trends-hourly': {
                'task': 'app.tasks.collectors.collect_all_trends',
                'schedule': crontab(minute=0),  # Toutes les heures
            },
            'analyze-trends-daily': {
                'task': 'app.tasks.analysis.analyze_global_trends',
                'schedule': crontab(hour=0, minute=0),  # Tous les jours à minuit
            },
            'update-metrics-realtime': {
                'task': 'app.tasks.collectors.update_metrics',
                'schedule': timedelta(minutes=5),  # Toutes les 5 minutes
            },
        },
        
        # Options de tâche par défaut
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Europe/Paris',
        enable_utc=True,
        
        # Configuration des workers
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
        worker_max_memory_per_child=200000,  # 200MB
        
        # Gestion des erreurs
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        
        # File d'attente par défaut
        task_default_queue='default',
        
        # Files d'attente spécifiques
        task_queues={
            'collectors': {
                'exchange': 'collectors',
                'routing_key': 'collectors.#',
            },
            'analysis': {
                'exchange': 'analysis',
                'routing_key': 'analysis.#',
            },
            'metrics': {
                'exchange': 'metrics',
                'routing_key': 'metrics.#',
            },
        },
        
        # Routes des tâches
        task_routes={
            'app.tasks.collectors.*': {'queue': 'collectors'},
            'app.tasks.analysis.*': {'queue': 'analysis'},
            'app.tasks.metrics.*': {'queue': 'metrics'},
        },
    )

    if app:
        celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            if app:
                with app.app_context():
                    return self.run(*args, **kwargs)
            return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Crée l'instance Celery
celery_app = create_celery_app()

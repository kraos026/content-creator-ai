from celery import shared_task
from app.collectors.manager import CollectorManager
from app.models.trend import Trend
from app import db
import logging
from datetime import datetime, timedelta
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from textblob import TextBlob
import pandas as pd

logger = logging.getLogger(__name__)

@shared_task(
    name='app.tasks.analysis.analyze_global_trends',
    queue='analysis',
)
def analyze_global_trends():
    """Analyse globale des tendances sur toutes les plateformes."""
    try:
        # Récupère les tendances des dernières 24h
        trends = Trend.query.filter(
            Trend.detected_at >= datetime.utcnow() - timedelta(days=1)
        ).all()
        
        # Prépare les données pour l'analyse
        trend_data = []
        for trend in trends:
            trend_data.append({
                'id': trend.id,
                'platform': trend.platform,
                'keyword': trend.keyword,
                'volume': trend.volume,
                'engagement': trend.engagement,
                'growth_rate': trend.growth_rate,
                'sentiment_score': trend.sentiment_score,
            })
        
        if not trend_data:
            logger.warning("Aucune tendance à analyser")
            return
        
        df = pd.DataFrame(trend_data)
        
        # Analyse par plateforme
        platform_analysis = analyze_platform_performance(df)
        
        # Segmentation des tendances
        trend_segments = segment_trends(df)
        
        # Analyse des corrélations
        correlation_analysis = analyze_correlations(df)
        
        # Prédiction des tendances futures
        future_predictions = predict_trend_evolution(df)
        
        # Sauvegarde les résultats
        analysis_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'platform_analysis': platform_analysis,
            'trend_segments': trend_segments,
            'correlation_analysis': correlation_analysis,
            'future_predictions': future_predictions,
        }
        
        # Met à jour la base de données
        for trend in trends:
            segment = next(
                (s for s in trend_segments if trend.id in s['trend_ids']),
                None
            )
            if segment:
                trend.category = segment['name']
                trend.insights = {
                    'segment': segment['characteristics'],
                    'predicted_growth': next(
                        (p for p in future_predictions if p['trend_id'] == trend.id),
                        {}
                    ),
                }
        
        db.session.commit()
        
        return analysis_results
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse globale des tendances: {str(e)}")
        raise

def analyze_platform_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyse les performances par plateforme."""
    try:
        platform_stats = {}
        
        for platform in df['platform'].unique():
            platform_df = df[df['platform'] == platform]
            
            # Calcule les métriques moyennes
            avg_engagement = platform_df['engagement'].mean()
            avg_growth = platform_df['growth_rate'].mean()
            avg_sentiment = platform_df['sentiment_score'].mean()
            
            # Identifie les tendances les plus performantes
            top_trends = platform_df.nlargest(5, 'engagement')[
                ['keyword', 'engagement', 'growth_rate']
            ].to_dict('records')
            
            # Analyse la distribution des engagements
            engagement_distribution = {
                'mean': avg_engagement,
                'median': platform_df['engagement'].median(),
                'std': platform_df['engagement'].std(),
                'quartiles': platform_df['engagement'].quantile([0.25, 0.75]).to_dict(),
            }
            
            platform_stats[platform] = {
                'metrics': {
                    'avg_engagement': avg_engagement,
                    'avg_growth_rate': avg_growth,
                    'avg_sentiment': avg_sentiment,
                },
                'top_trends': top_trends,
                'engagement_distribution': engagement_distribution,
            }
        
        return platform_stats
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des performances par plateforme: {str(e)}")
        raise

def segment_trends(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Segmente les tendances en clusters."""
    try:
        # Prépare les features pour le clustering
        features = ['volume', 'engagement', 'growth_rate', 'sentiment_score']
        X = df[features].values
        
        # Normalise les données
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Détermine le nombre optimal de clusters
        n_clusters = min(5, len(df))
        
        # Applique K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Analyse chaque segment
        segments = []
        for i in range(n_clusters):
            cluster_mask = clusters == i
            cluster_df = df[cluster_mask]
            
            # Caractéristiques moyennes du segment
            characteristics = {
                feature: cluster_df[feature].mean()
                for feature in features
            }
            
            # Tendances représentatives
            representative_trends = cluster_df.nlargest(3, 'engagement')[
                ['id', 'keyword', 'platform']
            ].to_dict('records')
            
            segments.append({
                'name': f"Segment {i+1}",
                'size': len(cluster_df),
                'characteristics': characteristics,
                'representative_trends': representative_trends,
                'trend_ids': cluster_df['id'].tolist(),
            })
        
        return segments
        
    except Exception as e:
        logger.error(f"Erreur lors de la segmentation des tendances: {str(e)}")
        raise

def analyze_correlations(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyse les corrélations entre les métriques."""
    try:
        # Calcule la matrice de corrélation
        correlation_matrix = df[
            ['volume', 'engagement', 'growth_rate', 'sentiment_score']
        ].corr()
        
        # Identifie les corrélations significatives
        significant_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr = correlation_matrix.iloc[i, j]
                if abs(corr) > 0.5:  # Seuil de corrélation significative
                    significant_correlations.append({
                        'metric1': correlation_matrix.columns[i],
                        'metric2': correlation_matrix.columns[j],
                        'correlation': corr,
                    })
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'significant_correlations': significant_correlations,
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des corrélations: {str(e)}")
        raise

def predict_trend_evolution(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Prédit l'évolution future des tendances."""
    try:
        predictions = []
        
        for _, trend in df.iterrows():
            # Facteurs de prédiction
            engagement_momentum = trend['growth_rate']
            sentiment_factor = (trend['sentiment_score'] + 1) / 2  # Normalise entre 0 et 1
            volume_factor = np.log1p(trend['volume']) / np.log1p(df['volume'].max())
            
            # Score composite
            potential_score = (
                0.4 * engagement_momentum +
                0.3 * sentiment_factor +
                0.3 * volume_factor
            )
            
            # Catégorise la prédiction
            if potential_score > 0.7:
                prediction = "forte_croissance"
                expected_growth = ">100%"
            elif potential_score > 0.5:
                prediction = "croissance_moderee"
                expected_growth = "50-100%"
            elif potential_score > 0.3:
                prediction = "stable"
                expected_growth = "0-50%"
            else:
                prediction = "declin"
                expected_growth = "<0%"
            
            predictions.append({
                'trend_id': trend['id'],
                'keyword': trend['keyword'],
                'platform': trend['platform'],
                'prediction': prediction,
                'expected_growth': expected_growth,
                'confidence_score': potential_score,
                'factors': {
                    'engagement_momentum': engagement_momentum,
                    'sentiment_factor': sentiment_factor,
                    'volume_factor': volume_factor,
                },
            })
        
        return predictions
        
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction de l'évolution des tendances: {str(e)}")
        raise

@shared_task(
    name='app.tasks.analysis.analyze_content_performance',
    queue='analysis',
)
def analyze_content_performance(content_id: str, platform: str):
    """Analyse approfondie des performances d'un contenu."""
    try:
        # Initialise le gestionnaire
        manager = CollectorManager({
            'tiktok': os.environ.get('TIKTOK_API_KEY'),
            'youtube': os.environ.get('YOUTUBE_API_KEY'),
            'instagram': os.environ.get('INSTAGRAM_API_KEY'),
            'facebook': os.environ.get('FACEBOOK_API_KEY'),
        })
        
        # Récupère le collecteur approprié
        collector = manager.collectors.get(platform)
        if not collector:
            raise ValueError(f"Plateforme non supportée: {platform}")
        
        # Analyse le contenu
        loop = asyncio.get_event_loop()
        analysis = loop.run_until_complete(
            collector.analyze_content_performance(content_id)
        )
        
        return {
            'content_id': content_id,
            'platform': platform,
            'timestamp': datetime.utcnow().isoformat(),
            'analysis': analysis,
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du contenu {content_id}: {str(e)}")
        raise

@shared_task(
    name='app.tasks.analysis.analyze_sentiment',
    queue='analysis',
)
def analyze_sentiment():
    """Analyse le sentiment des tendances actives."""
    try:
        # Récupère les tendances sans score de sentiment
        trends = Trend.query.filter(
            Trend.sentiment_score.is_(None),
            Trend.detected_at >= datetime.utcnow() - timedelta(days=1)
        ).all()
        
        for trend in trends:
            try:
                # Analyse le sentiment du mot-clé
                blob = TextBlob(trend.keyword)
                sentiment_score = blob.sentiment.polarity
                
                # Met à jour le score
                trend.sentiment_score = sentiment_score
                
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse du sentiment pour {trend.id}: {str(e)}")
                continue
        
        # Sauvegarde les modifications
        try:
            db.session.commit()
            logger.info(f"Sentiment analysé pour {len(trends)} tendances")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la sauvegarde des scores de sentiment: {str(e)}")
            raise
        
        return {'analyzed_trends': len(trends)}
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du sentiment: {str(e)}")
        raise

from typing import List, Dict
import numpy as np
from transformers import pipeline
from app.models.trend import Trend
from app import db

class TrendAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        
    async def analyze_platform_trends(self, platform: str) -> List[Dict]:
        """Analyse les tendances pour une plateforme spécifique."""
        try:
            # Collecter les données brutes de la plateforme
            raw_data = await self._collect_platform_data(platform)
            
            # Analyser les tendances
            trends = []
            for data in raw_data:
                trend = self._process_trend_data(data, platform)
                if trend:
                    trends.append(trend)
                    
            # Sauvegarder en base de données
            self._save_trends(trends)
            
            return [trend.to_dict() for trend in trends]
        
        except Exception as e:
            print(f"Erreur lors de l'analyse des tendances: {str(e)}")
            return []
    
    async def _collect_platform_data(self, platform: str) -> List[Dict]:
        """Collecte les données brutes d'une plateforme."""
        # TODO: Implémenter la collecte spécifique à chaque plateforme
        if platform == "tiktok":
            return await self._collect_tiktok_data()
        elif platform == "youtube":
            return await self._collect_youtube_data()
        elif platform == "facebook":
            return await self._collect_facebook_data()
        return []
    
    def _process_trend_data(self, data: Dict, platform: str) -> Trend:
        """Traite les données brutes pour créer un objet Trend."""
        try:
            # Analyse du sentiment
            sentiment = self.sentiment_analyzer(data['text'])[0]
            sentiment_score = self._normalize_sentiment_score(sentiment['score'])
            
            # Calcul du taux d'engagement
            engagement = self._calculate_engagement(data)
            
            # Création de l'objet Trend
            trend = Trend(
                platform=platform,
                keyword=data['keyword'],
                category=self._detect_category(data),
                volume=data.get('volume', 0),
                engagement=engagement,
                growth_rate=self._calculate_growth_rate(data),
                sentiment_score=sentiment_score,
                hashtags=data.get('hashtags', []),
                related_keywords=self._extract_related_keywords(data),
                peak_hours=self._analyze_peak_hours(data)
            )
            
            return trend
            
        except Exception as e:
            print(f"Erreur lors du traitement des données: {str(e)}")
            return None
    
    def _normalize_sentiment_score(self, score: float) -> float:
        """Normalise le score de sentiment entre -1 et 1."""
        return (score * 2) - 1
    
    def _calculate_engagement(self, data: Dict) -> int:
        """Calcule le score d'engagement total."""
        likes = data.get('likes', 0)
        comments = data.get('comments', 0)
        shares = data.get('shares', 0)
        return likes + (comments * 2) + (shares * 3)
    
    def _calculate_growth_rate(self, data: Dict) -> float:
        """Calcule le taux de croissance d'une tendance."""
        previous = data.get('previous_volume', 0)
        current = data.get('current_volume', 0)
        if previous == 0:
            return 100.0
        return ((current - previous) / previous) * 100
    
    def _detect_category(self, data: Dict) -> str:
        """Détecte la catégorie du contenu."""
        # TODO: Implémenter la détection de catégorie
        return "general"
    
    def _extract_related_keywords(self, data: Dict) -> List[str]:
        """Extrait les mots-clés connexes."""
        # TODO: Implémenter l'extraction de mots-clés
        return []
    
    def _analyze_peak_hours(self, data: Dict) -> Dict:
        """Analyse les heures de pic d'engagement."""
        # TODO: Implémenter l'analyse des heures de pic
        return {"morning": 9, "evening": 18}
    
    def _save_trends(self, trends: List[Trend]):
        """Sauvegarde les tendances en base de données."""
        try:
            for trend in trends:
                db.session.add(trend)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la sauvegarde des tendances: {str(e)}")

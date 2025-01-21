from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

class BaseCollector(ABC):
    """Classe de base pour tous les collecteurs de données des réseaux sociaux."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._cache = {}
        self._cache_duration = 3600  # 1 heure en secondes
        
    @abstractmethod
    async def get_trending_topics(self, max_results: int = 50) -> Dict:
        """Récupère les sujets tendance."""
        pass
        
    @abstractmethod
    async def get_content_analysis(self, content_id: str) -> Dict:
        """Analyse un contenu spécifique."""
        pass
        
    @abstractmethod
    async def get_competitor_analysis(self, competitor_id: str) -> Dict:
        """Analyse un concurrent spécifique."""
        pass
        
    @abstractmethod
    async def get_audience_insights(self, content_ids: List[str]) -> Dict:
        """Analyse l'audience d'un ensemble de contenus."""
        pass
        
    @abstractmethod
    async def generate_content_suggestions(self, category: str) -> List[Dict]:
        """Génère des suggestions de contenu."""
        pass
        
    def _cache_get(self, key: str) -> Optional[Dict]:
        """Récupère une valeur du cache."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if (datetime.now() - timestamp).seconds < self._cache_duration:
                return value
            del self._cache[key]
        return None
        
    def _cache_set(self, key: str, value: Dict):
        """Stocke une valeur dans le cache."""
        self._cache[key] = (value, datetime.now())
        
    def _calculate_engagement_rate(self, stats: Dict) -> float:
        """Calcule le taux d'engagement."""
        views = int(stats.get('views', 0))
        if views == 0:
            return 0.0
        interactions = sum(int(stats.get(metric, 0)) for metric in ['likes', 'comments', 'shares'])
        return interactions / views
        
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés d'un texte."""
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [word for word in words if word.isalnum() and word not in stop_words]
        
    def _get_performance_level(self, engagement_rate: float) -> str:
        """Détermine le niveau de performance."""
        if engagement_rate >= 0.1:
            return "Excellent"
        elif engagement_rate >= 0.05:
            return "Good"
        elif engagement_rate >= 0.02:
            return "Average"
        return "Poor"

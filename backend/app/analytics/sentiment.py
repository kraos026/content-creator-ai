from typing import Dict, List, Tuple
from collections import Counter
import re
from textblob import TextBlob
import emoji

class SentimentAnalyzer:
    def __init__(self):
        self.emoji_sentiment = {
            '❤️': 1.0, '😊': 0.8, '😂': 0.6,
            '😢': -0.5, '😡': -1.0, '👎': -0.8,
            '👍': 0.8, '🔥': 0.9, '💯': 1.0
        }
    
    async def analyze_comments(self, comments: List[Dict]) -> Dict:
        """Analyse complète des commentaires avec sentiment et thèmes."""
        sentiments = []
        themes = []
        emojis = []
        
        for comment in comments:
            text = comment.get('text', '')
            
            # Analyse du sentiment
            sentiment = self._get_sentiment(text)
            sentiments.append(sentiment)
            
            # Extraction des thèmes
            comment_themes = self._extract_themes(text)
            themes.extend(comment_themes)
            
            # Analyse des emojis
            comment_emojis = self._extract_emojis(text)
            emojis.extend(comment_emojis)
        
        return {
            'sentiment_stats': self._calculate_sentiment_stats(sentiments),
            'top_themes': self._get_top_items(themes, 5),
            'top_emojis': self._get_top_items(emojis, 5),
            'engagement_quality': self._calculate_engagement_quality(sentiments, emojis)
        }
    
    def _get_sentiment(self, text: str) -> float:
        """Calcule le sentiment d'un texte (-1 à 1)."""
        # Analyse du texte
        blob = TextBlob(text)
        text_sentiment = blob.sentiment.polarity
        
        # Analyse des emojis
        emojis = self._extract_emojis(text)
        emoji_sentiment = sum(self.emoji_sentiment.get(e, 0) for e in emojis) / max(len(emojis), 1)
        
        # Combiner les deux scores (70% texte, 30% emoji)
        return 0.7 * text_sentiment + 0.3 * emoji_sentiment
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extrait les thèmes principaux d'un commentaire."""
        # Nettoyer le texte
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        
        # Extraire les n-grams pertinents
        words = text.split()
        bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
        
        # Filtrer les mots/phrases non pertinents
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to'}
        themes = [w for w in words + bigrams if w not in stopwords and len(w) > 3]
        
        return themes
    
    def _extract_emojis(self, text: str) -> List[str]:
        """Extrait les emojis d'un texte."""
        return [c for c in text if c in emoji.EMOJI_DATA]
    
    def _calculate_sentiment_stats(self, sentiments: List[float]) -> Dict:
        """Calcule les statistiques de sentiment."""
        if not sentiments:
            return {'positive': 0, 'neutral': 0, 'negative': 0, 'average': 0}
        
        positive = sum(1 for s in sentiments if s > 0.2)
        negative = sum(1 for s in sentiments if s < -0.2)
        neutral = len(sentiments) - positive - negative
        
        return {
            'positive': (positive / len(sentiments)) * 100,
            'neutral': (neutral / len(sentiments)) * 100,
            'negative': (negative / len(sentiments)) * 100,
            'average': sum(sentiments) / len(sentiments)
        }
    
    def _get_top_items(self, items: List[str], n: int) -> List[Tuple[str, int]]:
        """Retourne les n éléments les plus fréquents."""
        counter = Counter(items)
        return counter.most_common(n)
    
    def _calculate_engagement_quality(self, sentiments: List[float], emojis: List[str]) -> float:
        """Calcule un score de qualité d'engagement (0 à 100)."""
        if not sentiments:
            return 0
        
        # Facteurs de qualité
        sentiment_score = (sum(sentiments) / len(sentiments) + 1) * 50  # -1 à 1 -> 0 à 100
        emoji_diversity = len(set(emojis)) / max(len(emojis), 1) * 100
        emoji_positivity = sum(self.emoji_sentiment.get(e, 0) for e in emojis) / max(len(emojis), 1) * 50 + 50
        
        # Score final pondéré
        quality_score = (
            0.5 * sentiment_score +
            0.3 * emoji_diversity +
            0.2 * emoji_positivity
        )
        
        return min(max(quality_score, 0), 100)  # Limiter entre 0 et 100

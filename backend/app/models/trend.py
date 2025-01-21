from datetime import datetime
from app import db

class Trend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(32), nullable=False)
    keyword = db.Column(db.String(128), nullable=False)
    category = db.Column(db.String(64))
    volume = db.Column(db.Integer)  # Nombre de posts/vidéos
    engagement = db.Column(db.Integer)  # Likes + commentaires + partages
    growth_rate = db.Column(db.Float)  # Taux de croissance en %
    sentiment_score = db.Column(db.Float)  # Score de sentiment (-1 à 1)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Métadonnées supplémentaires
    hashtags = db.Column(db.JSON)  # Liste des hashtags associés
    related_keywords = db.Column(db.JSON)  # Mots-clés connexes
    peak_hours = db.Column(db.JSON)  # Heures de pic d'engagement
    
    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'keyword': self.keyword,
            'category': self.category,
            'volume': self.volume,
            'engagement': self.engagement,
            'growth_rate': self.growth_rate,
            'sentiment_score': self.sentiment_score,
            'hashtags': self.hashtags,
            'related_keywords': self.related_keywords,
            'peak_hours': self.peak_hours,
            'detected_at': self.detected_at.isoformat()
        }

class ContentIdea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    target_platform = db.Column(db.String(32))
    estimated_virality = db.Column(db.Float)  # Score de 0 à 1
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Détails du contenu
    script = db.Column(db.Text)  # Script généré
    thumbnail_url = db.Column(db.String(512))  # URL de la miniature générée
    music_suggestions = db.Column(db.JSON)  # Liste des musiques suggérées
    tags = db.Column(db.JSON)  # Tags recommandés
    
    # Statut
    is_used = db.Column(db.Boolean, default=False)
    performance_score = db.Column(db.Float, nullable=True)  # Score réel après publication
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'target_platform': self.target_platform,
            'estimated_virality': self.estimated_virality,
            'script': self.script,
            'thumbnail_url': self.thumbnail_url,
            'music_suggestions': self.music_suggestions,
            'tags': self.tags,
            'is_used': self.is_used,
            'performance_score': self.performance_score,
            'generated_at': self.generated_at.isoformat()
        }

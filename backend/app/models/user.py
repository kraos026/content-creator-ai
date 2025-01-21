from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Préférences de contenu
    content_niche = db.Column(db.String(64))
    preferred_platforms = db.Column(db.JSON)
    posting_frequency = db.Column(db.String(32))
    
    # Statistiques
    total_videos = db.Column(db.Integer, default=0)
    total_views = db.Column(db.Integer, default=0)
    average_engagement_rate = db.Column(db.Float, default=0.0)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'content_niche': self.content_niche,
            'preferred_platforms': self.preferred_platforms,
            'posting_frequency': self.posting_frequency,
            'total_videos': self.total_videos,
            'total_views': self.total_views,
            'average_engagement_rate': self.average_engagement_rate,
            'created_at': self.created_at.isoformat()
        }

from typing import Dict, List
import openai
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from app.models.trend import ContentIdea
from app import db

class ContentGenerator:
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        
    async def generate_content_ideas(self, user_id: int, niche: str, trends: List[Dict]) -> List[ContentIdea]:
        """Génère des idées de contenu basées sur les tendances et la niche de l'utilisateur."""
        try:
            # Analyse des tendances pertinentes
            relevant_trends = self._filter_relevant_trends(trends, niche)
            
            # Génération d'idées avec GPT-4
            ideas = []
            for trend in relevant_trends:
                idea = await self._generate_idea(user_id, trend, niche)
                if idea:
                    ideas.append(idea)
            
            # Sauvegarde en base de données
            self._save_ideas(ideas)
            
            return ideas
            
        except Exception as e:
            print(f"Erreur lors de la génération d'idées: {str(e)}")
            return []
    
    def _filter_relevant_trends(self, trends: List[Dict], niche: str) -> List[Dict]:
        """Filtre les tendances pertinentes pour la niche donnée."""
        return [
            trend for trend in trends
            if self._calculate_relevance_score(trend, niche) > 0.7
        ]
    
    async def _generate_idea(self, user_id: int, trend: Dict, niche: str) -> ContentIdea:
        """Génère une idée de contenu complète basée sur une tendance."""
        try:
            # Génération du titre et de la description
            prompt = self._create_idea_prompt(trend, niche)
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Vous êtes un expert en création de contenu viral."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content
            title, description = self._parse_gpt_response(content)
            
            # Génération du script
            script = await self._generate_script(title, description, trend['platform'])
            
            # Génération de la miniature
            thumbnail_url = await self._generate_thumbnail(title, trend['platform'])
            
            # Suggestions musicales
            music_suggestions = self._suggest_music(trend)
            
            # Création de l'objet ContentIdea
            idea = ContentIdea(
                user_id=user_id,
                title=title,
                description=description,
                target_platform=trend['platform'],
                estimated_virality=self._estimate_virality(trend),
                script=script,
                thumbnail_url=thumbnail_url,
                music_suggestions=music_suggestions,
                tags=self._generate_tags(title, description, trend)
            )
            
            return idea
            
        except Exception as e:
            print(f"Erreur lors de la génération d'une idée: {str(e)}")
            return None
    
    def _create_idea_prompt(self, trend: Dict, niche: str) -> str:
        """Crée un prompt pour la génération d'idées."""
        return f"""
        En tant qu'expert en création de contenu viral pour {trend['platform']},
        générez une idée de vidéo dans la niche {niche} basée sur la tendance suivante:
        
        Mot-clé: {trend['keyword']}
        Engagement: {trend['engagement']}
        Sentiment: {trend['sentiment_score']}
        
        La réponse doit inclure:
        1. Un titre accrocheur (max 60 caractères)
        2. Une description engageante (max 200 caractères)
        
        Format de réponse:
        TITRE: [votre titre]
        DESCRIPTION: [votre description]
        """
    
    def _parse_gpt_response(self, response: str) -> tuple:
        """Parse la réponse de GPT pour extraire le titre et la description."""
        lines = response.strip().split('\n')
        title = lines[0].replace('TITRE:', '').strip()
        description = lines[1].replace('DESCRIPTION:', '').strip()
        return title, description
    
    async def _generate_script(self, title: str, description: str, platform: str) -> str:
        """Génère un script optimisé pour la plateforme cible."""
        try:
            prompt = f"""
            Créez un script pour une vidéo {platform} avec:
            Titre: {title}
            Description: {description}
            
            Le script doit inclure:
            1. Une accroche forte (5 secondes)
            2. Le contenu principal
            3. Un call-to-action engageant
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Vous êtes un scénariste expert en vidéos virales."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Erreur lors de la génération du script: {str(e)}")
            return ""
    
    async def _generate_thumbnail(self, title: str, platform: str) -> str:
        """Génère une miniature optimisée."""
        # TODO: Implémenter la génération de miniatures avec DALL-E ou un service similaire
        return "url_placeholder"
    
    def _suggest_music(self, trend: Dict) -> List[Dict]:
        """Suggère des musiques populaires pour la vidéo."""
        # TODO: Implémenter les suggestions de musique
        return []
    
    def _estimate_virality(self, trend: Dict) -> float:
        """Estime le potentiel viral d'une idée."""
        engagement_weight = 0.4
        sentiment_weight = 0.3
        growth_weight = 0.3
        
        normalized_engagement = min(trend['engagement'] / 10000, 1)
        normalized_sentiment = (trend['sentiment_score'] + 1) / 2
        normalized_growth = min(trend['growth_rate'] / 100, 1)
        
        virality_score = (
            engagement_weight * normalized_engagement +
            sentiment_weight * normalized_sentiment +
            growth_weight * normalized_growth
        )
        
        return round(virality_score, 2)
    
    def _generate_tags(self, title: str, description: str, trend: Dict) -> List[str]:
        """Génère des tags optimisés pour le référencement."""
        # Combine tous les textes pertinents
        text = f"{title} {description} {trend['keyword']}"
        
        # Extraction des hashtags existants
        existing_tags = trend.get('hashtags', [])
        
        # TODO: Implémenter une meilleure extraction de tags
        # Pour l'instant, on retourne juste les hashtags existants
        return existing_tags
    
    def _save_ideas(self, ideas: List[ContentIdea]):
        """Sauvegarde les idées en base de données."""
        try:
            for idea in ideas:
                db.session.add(idea)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la sauvegarde des idées: {str(e)}")

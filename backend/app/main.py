from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from .collectors.youtube import YouTubeCollector
from .collectors.facebook import FacebookCollector
from .collectors.douyin import DouyinCollector
from .analytics.performance import PerformanceAnalyzer
from .analytics.sentiment import SentimentAnalyzer
from .generators.content import ContentGenerator
from pydantic import BaseModel

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(
    title="Content Creator AI API",
    description="API pour l'analyse et l'optimisation de contenu sur les réseaux sociaux",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dépendances pour les collecteurs
def get_youtube_collector():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="YouTube API key not configured")
    return YouTubeCollector(api_key)

def get_facebook_collector():
    api_key = os.getenv("FACEBOOK_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Facebook API key not configured")
    return FacebookCollector(api_key)

def get_douyin_collector():
    api_key = os.getenv("DOUYIN_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Douyin API key not configured")
    return DouyinCollector(api_key)

# Routes pour l'analyse des tendances
@app.get("/trends/{platform}", response_model=Dict)
async def get_trends(
    platform: str,
    max_results: int = 50,
    youtube: Optional[YouTubeCollector] = Depends(get_youtube_collector),
    facebook: Optional[FacebookCollector] = Depends(get_facebook_collector),
    douyin: Optional[DouyinCollector] = Depends(get_douyin_collector)
):
    """Récupère les tendances pour une plateforme donnée."""
    collectors = {
        'youtube': youtube,
        'facebook': facebook,
        'douyin': douyin
    }
    
    if platform not in collectors:
        raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")
        
    try:
        return await collectors[platform].get_trending_topics(max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Routes pour l'analyse de contenu
@app.get("/{platform}/content/{content_id}", response_model=Dict)
async def analyze_content(
    platform: str,
    content_id: str,
    youtube: Optional[YouTubeCollector] = Depends(get_youtube_collector),
    facebook: Optional[FacebookCollector] = Depends(get_facebook_collector),
    douyin: Optional[DouyinCollector] = Depends(get_douyin_collector)
):
    """Analyse un contenu spécifique."""
    collectors = {
        'youtube': youtube,
        'facebook': facebook,
        'douyin': douyin
    }
    
    if platform not in collectors:
        raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")
        
    try:
        return await collectors[platform].get_content_analysis(content_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Routes pour l'analyse des concurrents
@app.get("/{platform}/competitor/{competitor_id}", response_model=Dict)
async def analyze_competitor(
    platform: str,
    competitor_id: str,
    youtube: Optional[YouTubeCollector] = Depends(get_youtube_collector),
    facebook: Optional[FacebookCollector] = Depends(get_facebook_collector),
    douyin: Optional[DouyinCollector] = Depends(get_douyin_collector)
):
    """Analyse un concurrent spécifique."""
    collectors = {
        'youtube': youtube,
        'facebook': facebook,
        'douyin': douyin
    }
    
    if platform not in collectors:
        raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")
        
    try:
        return await collectors[platform].get_competitor_analysis(competitor_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Routes pour les insights d'audience
@app.post("/{platform}/audience", response_model=Dict)
async def get_audience_insights(
    platform: str,
    content_ids: List[str],
    youtube: Optional[YouTubeCollector] = Depends(get_youtube_collector),
    facebook: Optional[FacebookCollector] = Depends(get_facebook_collector),
    douyin: Optional[DouyinCollector] = Depends(get_douyin_collector)
):
    """Analyse l'audience d'un ensemble de contenus."""
    collectors = {
        'youtube': youtube,
        'facebook': facebook,
        'douyin': douyin
    }
    
    if platform not in collectors:
        raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")
        
    try:
        return await collectors[platform].get_audience_insights(content_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Routes pour les suggestions de contenu
@app.get("/{platform}/suggestions/{category}", response_model=List[Dict])
async def get_content_suggestions(
    platform: str,
    category: str,
    youtube: Optional[YouTubeCollector] = Depends(get_youtube_collector),
    facebook: Optional[FacebookCollector] = Depends(get_facebook_collector),
    douyin: Optional[DouyinCollector] = Depends(get_douyin_collector)
):
    """Génère des suggestions de contenu pour une catégorie donnée."""
    collectors = {
        'youtube': youtube,
        'facebook': facebook,
        'douyin': douyin
    }
    
    if platform not in collectors:
        raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")
        
    try:
        return await collectors[platform].generate_content_suggestions(category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Nouveaux endpoints pour l'analyse des performances
@app.post("/{platform}/performance/best-times")
async def get_best_posting_times(
    platform: str,
    collector: BaseCollector = Depends(get_collector),
    days: int = Query(default=30, ge=1, le=90)
):
    analyzer = PerformanceAnalyzer(collector)
    content_data = await collector.get_content_history(days)
    return await analyzer.analyze_best_posting_times(content_data, days)

@app.post("/{platform}/performance/virality")
async def predict_virality(
    platform: str,
    content_data: Dict,
    collector: BaseCollector = Depends(get_collector)
):
    analyzer = PerformanceAnalyzer(collector)
    return {"virality_score": await analyzer.predict_virality(content_data)}

@app.post("/{platform}/performance/calendar")
async def generate_content_calendar(
    platform: str,
    topics: List[str],
    frequency: int = Query(default=3, ge=1, le=7),
    collector: BaseCollector = Depends(get_collector)
):
    analyzer = PerformanceAnalyzer(collector)
    return await analyzer.generate_content_calendar(topics, frequency)

# Nouveaux endpoints pour l'analyse des sentiments
@app.post("/{platform}/sentiment/comments")
async def analyze_comments(
    platform: str,
    comments: List[Dict],
    collector: BaseCollector = Depends(get_collector)
):
    analyzer = SentimentAnalyzer()
    return await analyzer.analyze_comments(comments)

# Nouveaux endpoints pour la génération de contenu
@app.post("/{platform}/content/brief")
async def generate_content_brief(
    platform: str,
    topic: str,
    content_type: str = Query(..., enum=["tutorial", "review", "story"]),
    collector: BaseCollector = Depends(get_collector)
):
    generator = ContentGenerator()
    return generator.generate_content_brief(topic, platform, content_type)

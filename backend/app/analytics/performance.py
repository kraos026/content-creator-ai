from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..collectors.base import BaseCollector

class PerformanceAnalyzer:
    def __init__(self, collector: BaseCollector):
        self.collector = collector
        
    async def analyze_best_posting_times(self, content_data: List[Dict[str, Any]], days: int = 30) -> Dict[str, List[int]]:
        if not content_data:
            return {
                "Monday": [9, 12, 15],
                "Tuesday": [10, 14, 16],
                "Wednesday": [9, 13, 17],
                "Thursday": [11, 14, 16],
                "Friday": [10, 12, 15],
                "Saturday": [11, 14, 17],
                "Sunday": [12, 15, 18]
            }
            
        df = pd.DataFrame(content_data)
        df['posted_at'] = pd.to_datetime(df['posted_at'])
        df['day'] = df['posted_at'].dt.day_name()
        df['hour'] = df['posted_at'].dt.hour
        
        best_times = {}
        for day in df['day'].unique():
            day_data = df[df['day'] == day]
            best_hours = day_data.groupby('hour')['engagement_rate'].mean().nlargest(3).index.tolist()
            best_times[day] = best_hours
        
        return best_times
    
    async def predict_virality(self, content_data: Dict[str, Any]) -> float:
        # Simple virality score based on engagement metrics
        engagement_rate = content_data.get('engagement_rate', 0)
        views = content_data.get('view_count', 0)
        comments = content_data.get('comment_count', 0)
        shares = content_data.get('share_count', 0)
        
        # Normalize metrics
        max_engagement = 100
        max_views = 1000000
        max_comments = 10000
        max_shares = 5000
        
        normalized_engagement = min(engagement_rate / max_engagement, 1)
        normalized_views = min(views / max_views, 1)
        normalized_comments = min(comments / max_comments, 1)
        normalized_shares = min(shares / max_shares, 1)
        
        # Calculate weighted score
        weights = {
            'engagement': 0.4,
            'views': 0.2,
            'comments': 0.2,
            'shares': 0.2
        }
        
        virality_score = (
            weights['engagement'] * normalized_engagement +
            weights['views'] * normalized_views +
            weights['comments'] * normalized_comments +
            weights['shares'] * normalized_shares
        ) * 100
        
        return virality_score
    
    async def generate_content_calendar(self, topics: List[str], frequency: int = 3) -> List[Dict[str, Any]]:
        best_times = await self.analyze_best_posting_times([])
        calendar = []
        
        start_date = datetime.now()
        for i in range(30):  # Generate calendar for next 30 days
            current_date = start_date + timedelta(days=i)
            day_name = current_date.strftime('%A')
            
            if day_name in best_times:
                posting_times = best_times[day_name][:frequency]
                
                for hour in posting_times:
                    topic = np.random.choice(topics)
                    platform = np.random.choice(['youtube', 'tiktok', 'instagram'])
                    content_type = np.random.choice(['tutorial', 'review', 'story'])
                    
                    calendar.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'time': f"{hour:02d}:00",
                        'topic': topic,
                        'platform': platform,
                        'content_type': content_type,
                        'suggested_hashtags': [f"#{topic.lower().replace(' ', '')}", "#content", f"#{platform}"]
                    })
        
        return calendar
    
    def _suggest_content_type(self, topic: str) -> str:
        """Suggère le type de contenu optimal pour un sujet."""
        content_types = ['tutorial', 'review', 'behind_the_scenes', 'tips', 'story']
        # Logique simple - à améliorer avec ML
        if 'how' in topic.lower() or 'guide' in topic.lower():
            return 'tutorial'
        if 'review' in topic.lower() or 'vs' in topic.lower():
            return 'review'
        if 'day' in topic.lower() or 'life' in topic.lower():
            return 'behind_the_scenes'
        if 'tips' in topic.lower() or 'tricks' in topic.lower():
            return 'tips'
        return 'story'
    
    def _generate_hashtags(self, topic: str, max_hashtags: int = 5) -> List[str]:
        """Génère des hashtags pertinents pour un sujet."""
        words = topic.lower().split()
        hashtags = [f'#{word}' for word in words if len(word) > 3]
        
        # Ajouter des hashtags génériques selon le type de contenu
        content_type = self._suggest_content_type(topic)
        generic_hashtags = {
            'tutorial': ['#howto', '#tutorial', '#learn'],
            'review': ['#review', '#honest', '#opinion'],
            'behind_the_scenes': ['#bts', '#behindthescenes', '#dayinthelife'],
            'tips': ['#tips', '#advice', '#protip'],
            'story': ['#story', '#experience', '#journey']
        }
        
        hashtags.extend(generic_hashtags.get(content_type, [])[:max_hashtags - len(hashtags)])
        return hashtags[:max_hashtags]

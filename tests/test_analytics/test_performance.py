import pytest
from datetime import datetime, timedelta
from backend.app.analytics.performance import PerformanceAnalyzer
from backend.app.collectors.base import BaseCollector

class MockCollector(BaseCollector):
    def __init__(self):
        super().__init__(api_key="test_api_key")
    
    async def get_trending_topics(self):
        return ["Python", "AI", "Web Development"]
    
    async def analyze_content(self, content_id: str):
        return {"engagement_rate": 15.5}
    
    async def get_content_history(self, days: int):
        now = datetime.now()
        return [
            {
                "posted_at": (now - timedelta(days=i)).isoformat(),
                "engagement_rate": 10 + i,
                "view_count": 1000 * i,
                "comment_count": 100 * i,
                "share_count": 50 * i,
                "hashtags": ["python", "coding"],
                "description": "Test video description"
            }
            for i in range(days)
        ]
    
    async def get_content_analysis(self, content_id: str):
        return {
            "engagement_rate": 15.5,
            "views": 10000,
            "likes": 1000,
            "comments": 500,
            "shares": 200,
            "sentiment": 0.8,
            "topics": ["Python", "Programming", "Tutorial"]
        }
    
    async def get_competitor_analysis(self, competitor_id: str):
        return {
            "engagement_rate": 12.5,
            "followers": 50000,
            "content_frequency": 3,
            "top_content": [
                {"id": "1", "engagement_rate": 20.5},
                {"id": "2", "engagement_rate": 18.2}
            ]
        }
    
    async def get_audience_insights(self):
        return {
            "demographics": {
                "age": {"18-24": 30, "25-34": 45},
                "gender": {"male": 70, "female": 30}
            },
            "interests": ["Technology", "Programming", "Education"],
            "active_times": {
                "days": {"Monday": 15, "Friday": 20},
                "hours": {"9": 10, "15": 15}
            }
        }
    
    async def generate_content_suggestions(self, category: str = None):
        return [
            {
                "title": "10 Python Tips for Beginners",
                "description": "Essential Python tips for new programmers",
                "type": "tutorial",
                "estimated_engagement": 15.5
            },
            {
                "title": "Building an AI App with Python",
                "description": "Step-by-step AI application tutorial",
                "type": "tutorial",
                "estimated_engagement": 18.2
            }
        ]

@pytest.fixture
def performance_analyzer():
    collector = MockCollector()
    return PerformanceAnalyzer(collector)

@pytest.mark.asyncio
async def test_analyze_best_posting_times(performance_analyzer):
    best_times = await performance_analyzer.analyze_best_posting_times(
        await performance_analyzer.collector.get_content_history(30),
        days=30
    )
    
    assert isinstance(best_times, dict)
    assert len(best_times) > 0
    for day, hours in best_times.items():
        assert isinstance(day, str)
        assert isinstance(hours, list)
        assert all(isinstance(h, int) for h in hours)
        assert all(0 <= h <= 23 for h in hours)

@pytest.mark.asyncio
async def test_predict_virality(performance_analyzer):
    content_data = {
        "engagement_rate": 15.5,
        "view_count": 10000,
        "comment_count": 500,
        "share_count": 200,
        "hashtags": ["python", "coding"],
        "description": "Test video description"
    }
    
    virality_score = await performance_analyzer.predict_virality(content_data)
    
    assert isinstance(virality_score, float)
    assert 0 <= virality_score <= 100

@pytest.mark.asyncio
async def test_generate_content_calendar(performance_analyzer):
    topics = ["Python", "AI", "Web Development"]
    calendar = await performance_analyzer.generate_content_calendar(topics, frequency=3)
    
    assert isinstance(calendar, list)
    assert len(calendar) > 0
    for entry in calendar:
        assert isinstance(entry, dict)
        assert all(key in entry for key in ['date', 'time', 'topic', 'platform', 'content_type', 'suggested_hashtags'])
        assert datetime.strptime(entry['date'], '%Y-%m-%d')
        assert datetime.strptime(entry['time'], '%H:%M')
        assert entry['topic'] in topics
        assert isinstance(entry['suggested_hashtags'], list)

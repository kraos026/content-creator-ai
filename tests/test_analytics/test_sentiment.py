import pytest
from backend.app.analytics.sentiment import SentimentAnalyzer

@pytest.fixture
def sentiment_analyzer():
    return SentimentAnalyzer()

@pytest.fixture
def sample_comments():
    return [
        {"text": "This is amazing! ❤️ Love your content! 🔥"},
        {"text": "Not really helpful... 👎"},
        {"text": "Great tutorial, very clear explanation 👍"},
        {"text": "Could be better 😐"},
        {"text": "This changed my life! Best content ever! ❤️😊"}
    ]

@pytest.mark.asyncio
async def test_analyze_comments(sentiment_analyzer, sample_comments):
    analysis = await sentiment_analyzer.analyze_comments(sample_comments)
    
    assert isinstance(analysis, dict)
    assert all(key in analysis for key in ['sentiment_stats', 'top_themes', 'top_emojis', 'engagement_quality'])
    
    # Test sentiment stats
    stats = analysis['sentiment_stats']
    assert all(key in stats for key in ['positive', 'neutral', 'negative', 'average'])
    assert all(isinstance(v, float) for v in stats.values())
    assert all(0 <= v <= 100 for v in [stats['positive'], stats['neutral'], stats['negative']])
    assert -1 <= stats['average'] <= 1
    
    # Test top themes
    assert isinstance(analysis['top_themes'], list)
    for theme, count in analysis['top_themes']:
        assert isinstance(theme, str)
        assert isinstance(count, int)
        assert count > 0
    
    # Test top emojis
    assert isinstance(analysis['top_emojis'], list)
    for emoji, count in analysis['top_emojis']:
        assert isinstance(emoji, str)
        assert isinstance(count, int)
        assert count > 0
    
    # Test engagement quality
    assert isinstance(analysis['engagement_quality'], float)
    assert 0 <= analysis['engagement_quality'] <= 100

def test_get_sentiment(sentiment_analyzer):
    # Test positive sentiment
    text = "This is amazing! ❤️ Love it! 🔥"
    sentiment = sentiment_analyzer._get_sentiment(text)
    assert isinstance(sentiment, float)
    assert sentiment > 0
    
    # Test negative sentiment
    text = "This is terrible... 👎 Hate it."
    sentiment = sentiment_analyzer._get_sentiment(text)
    assert isinstance(sentiment, float)
    assert sentiment < 0
    
    # Test neutral sentiment
    text = "This is okay. Not great, not terrible."
    sentiment = sentiment_analyzer._get_sentiment(text)
    assert isinstance(sentiment, float)
    assert -0.2 <= sentiment <= 0.2

def test_extract_themes(sentiment_analyzer):
    text = "Great Python tutorial for beginners! Love the coding examples."
    themes = sentiment_analyzer._extract_themes(text)
    
    assert isinstance(themes, list)
    assert len(themes) > 0
    assert all(isinstance(theme, str) for theme in themes)
    assert "python tutorial" in themes or "tutorial" in themes

def test_extract_emojis(sentiment_analyzer):
    text = "Love this! ❤️ Amazing content! 🔥 Keep it up! 👍"
    emojis = sentiment_analyzer._extract_emojis(text)
    
    assert isinstance(emojis, list)
    assert len(emojis) == 3
    assert any(emoji in emojis for emoji in ["❤️", "❤"])  # Accepter les deux versions
    assert "🔥" in emojis
    assert "👍" in emojis

def test_calculate_engagement_quality(sentiment_analyzer):
    sentiments = [0.8, 0.5, -0.2, 0.9, 0.3]
    emojis = ["❤️", "👍", "🔥", "😊"]
    
    quality = sentiment_analyzer._calculate_engagement_quality(sentiments, emojis)
    
    assert isinstance(quality, float)
    assert 0 <= quality <= 100

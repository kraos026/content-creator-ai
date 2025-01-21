import pytest
from unittest.mock import patch
from backend.app.collectors.youtube import YouTubeCollector
from backend.app.collectors.instagram import InstagramCollector
from backend.app.collectors.facebook import FacebookCollector
from backend.app.collectors.tiktok import TikTokCollector
from backend.app.collectors.douyin import DouyinCollector
from tests.conftest import MockClientSession

@pytest.mark.asyncio
async def test_youtube_trending_topics(mock_youtube_api_response):
    """Test la récupération des tendances YouTube."""
    async with MockClientSession({'https://www.googleapis.com/youtube/v3/videos': mock_youtube_api_response}) as session:
        with patch('aiohttp.ClientSession', return_value=session):
            collector = YouTubeCollector('test_key')
            trends = await collector.get_trending_topics()

            assert len(trends) > 0
            assert 'id' in trends[0]
            assert 'title' in trends[0]
            assert 'engagement_rate' in trends[0]
            assert trends[0]['engagement_rate'] > 0

@pytest.mark.asyncio
async def test_instagram_collector(mock_responses):
    """Test les fonctionnalités du collecteur Instagram."""
    async with MockClientSession(mock_responses) as session:
        with patch('aiohttp.ClientSession', return_value=session):
            collector = InstagramCollector('test_key')
            trends = await collector.get_trending_topics()

            assert len(trends) == 1
            assert trends[0]['id'] == '123456'
            assert trends[0]['caption'] == 'Un super post Instagram !'
            assert trends[0]['like_count'] == 1000
            assert trends[0]['comments_count'] == 50
            assert trends[0]['engagement_rate'] > 0
            assert trends[0]['performance_level'] == 'high'

@pytest.mark.asyncio
async def test_facebook_collector(mock_responses):
    """Test les fonctionnalités du collecteur Facebook."""
    async with MockClientSession(mock_responses) as session:
        with patch('aiohttp.ClientSession', return_value=session):
            collector = FacebookCollector('test_key')
            trends = await collector.get_trending_topics()

            assert len(trends) == 1
            assert trends[0]['id'] == '789012'
            assert trends[0]['message'] == 'Un super post Facebook !'
            assert trends[0]['likes'] == 800
            assert trends[0]['comments'] == 40
            assert trends[0]['shares'] == 15

@pytest.mark.asyncio
async def test_tiktok_collector(mock_responses):
    """Test les fonctionnalités du collecteur TikTok."""
    async with MockClientSession(mock_responses) as session:
        with patch('aiohttp.ClientSession', return_value=session):
            collector = TikTokCollector('test_key')
            trends = await collector.get_trending_topics()

            assert len(trends) == 1
            assert trends[0]['id'] == '345678'
            assert trends[0]['description'] == 'Une super vidéo TikTok !'
            assert trends[0]['digg_count'] == '1200'
            assert trends[0]['comment_count'] == '60'
            assert trends[0]['share_count'] == '25'
            assert trends[0]['play_count'] == '8000'

@pytest.mark.asyncio
async def test_douyin_collector(mock_douyin_api_response):
    """Test les fonctionnalités du collecteur Douyin."""
    async with MockClientSession(mock_douyin_api_response) as session:
        with patch('aiohttp.ClientSession', return_value=session):
            collector = DouyinCollector('test_key')

            # Test get_trending_topics
            trends = await collector.get_trending_topics()
            assert len(trends) > 0
            assert 'id' in trends[0]
            assert 'title' in trends[0]

            # Test get_content_details
            details = await collector.get_content_details('test_video_id')
            assert details['author']['uid'] == '12345'
            assert details['title'] == 'Test Video'

            # Test get_engagement_metrics
            metrics = await collector.get_engagement_metrics('test_video_id')
            assert metrics['engagement_rate'] > 0
            assert metrics['completion_rate'] > 0

@pytest.mark.asyncio
async def test_error_handling():
    """Test la gestion des erreurs pour tous les collecteurs."""
    error_responses = {
        "https://graph.instagram.com/v12.0/me/media": {"error": "Invalid token"},
        "https://graph.facebook.com/v12.0/me/posts": {"error": "Invalid token"},
        "https://api.tiktok.com/v1/videos/popular": {"error": "Invalid token"},
        "https://open.douyin.com/trending/hashtags": {"error": "Invalid token"}
    }

    endpoints = {
        InstagramCollector: "https://graph.instagram.com/v12.0/me/media",
        FacebookCollector: "https://graph.facebook.com/v12.0/me/posts",
        TikTokCollector: "https://api.tiktok.com/v1/videos/popular",
        DouyinCollector: "https://open.douyin.com/trending/hashtags"
    }

    async with MockClientSession(error_responses, status=401) as session:
        with patch('aiohttp.ClientSession', return_value=session):
            collectors = [
                InstagramCollector('test_key'),
                FacebookCollector('test_key'),
                TikTokCollector('test_key'),
                DouyinCollector('test_key')
            ]

            for collector in collectors:
                try:
                    await collector._make_request(
                        url=endpoints[type(collector)],
                        params={'error': True}
                    )
                    pytest.fail("Une exception aurait dû être levée")
                except Exception as e:
                    assert "Invalid token" in str(e)

@pytest.mark.asyncio
async def test_douyin_error_handling():
    """Test la gestion des erreurs du collecteur Douyin."""
    error_responses = {
        "https://open.douyin.com/trending/hashtags": {"error": "Invalid token"},
        "https://open.douyin.com/api/v1/video/info": {"error": "Video not found"},
        "https://open.douyin.com/api/v1/video/stats": {"error": "Stats not available"}
    }

    async with MockClientSession(error_responses, status=401) as session:
        with patch('aiohttp.ClientSession', return_value=session):
            collector = DouyinCollector('test_key')

            try:
                await collector._make_request(
                    url="https://open.douyin.com/trending/hashtags",
                    params={'error': True}
                )
                pytest.fail("Une exception aurait dû être levée")
            except Exception as e:
                assert "Invalid token" in str(e)

            try:
                await collector._make_request(
                    url="https://open.douyin.com/api/v1/video/info",
                    params={'error': True}
                )
                pytest.fail("Une exception aurait dû être levée")
            except Exception as e:
                assert "Video not found" in str(e)

            try:
                await collector._make_request(
                    url="https://open.douyin.com/api/v1/video/stats",
                    params={'error': True}
                )
                pytest.fail("Une exception aurait dû être levée")
            except Exception as e:
                assert "Stats not available" in str(e)

@pytest.mark.asyncio
async def test_douyin_sentiment_analysis():
    """Test l'analyse de sentiment du collecteur Douyin."""
    test_text = "这个视频太棒了！我非常喜欢！"  # "Cette vidéo est super ! J'adore !"
    collector = DouyinCollector('test_key')
    sentiment = collector._analyze_sentiment(test_text)
    assert isinstance(sentiment, float)
    assert 0 <= sentiment <= 1

@pytest.mark.asyncio
async def test_sentiment_analysis():
    """Test l'analyse de sentiment pour tous les collecteurs."""
    test_texts = [
        "This video is amazing! I love it!",  # Anglais
        "这个视频太棒了！我非常喜欢！",  # Chinois
        "Cette vidéo est super ! J'adore !"  # Français
    ]

    collectors = [
        InstagramCollector('test_key'),
        FacebookCollector('test_key'),
        TikTokCollector('test_key'),
        DouyinCollector('test_key')
    ]

    for collector in collectors:
        for text in test_texts:
            sentiment = collector._analyze_sentiment(text)
            assert isinstance(sentiment, float)
            assert 0 <= sentiment <= 1

@pytest.mark.asyncio
async def test_collector_session_cleanup(mock_responses):
    """Test le nettoyage correct des sessions."""
    session = MockClientSession(mock_responses)
    
    with patch('aiohttp.ClientSession', return_value=session):
        async with InstagramCollector('test_key') as collector:
            await collector.get_trending_topics()
            assert not session.closed
        
        assert session.closed

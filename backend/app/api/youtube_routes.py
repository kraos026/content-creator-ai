from flask import Blueprint, jsonify, request, current_app
from ..collectors.youtube import YouTubeCollector
import os
from datetime import datetime, timedelta

youtube_bp = Blueprint('youtube', __name__)

@youtube_bp.route('/trending', methods=['GET'])
async def get_trending():
    """Récupère les vidéos tendances."""
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        trends = await collector.get_trending_topics()
        return jsonify(trends)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/analyze/video/<video_id>', methods=['GET'])
async def analyze_video(video_id):
    """Analyse une vidéo spécifique."""
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        analysis = await collector.get_content_analysis(video_id)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/analyze/channel/<channel_id>', methods=['GET'])
async def analyze_channel(channel_id):
    """Analyse un canal YouTube."""
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        analysis = await collector.get_competitor_analysis(channel_id)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/suggestions', methods=['GET'])
async def get_suggestions():
    """Obtient des suggestions de contenu."""
    category = request.args.get('category', 'general')
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        suggestions = await collector.generate_content_suggestions(category)
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/audience', methods=['POST'])
async def analyze_audience():
    """Analyse l'audience basée sur une liste de vidéos."""
    video_ids = request.json.get('video_ids', [])
    if not video_ids:
        return jsonify({'error': 'video_ids requis'}), 400
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        insights = await collector.get_audience_insights(video_ids)
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Nouvelles routes

@youtube_bp.route('/keywords/analyze', methods=['POST'])
async def analyze_keywords():
    """Analyse les mots-clés pour un sujet donné."""
    keywords = request.json.get('keywords', [])
    if not keywords:
        return jsonify({'error': 'keywords requis'}), 400
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        analysis = await collector.analyze_keywords(keywords)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/schedule/optimal', methods=['GET'])
async def get_optimal_schedule():
    """Détermine les meilleurs moments pour publier."""
    channel_id = request.args.get('channel_id')
    if not channel_id:
        return jsonify({'error': 'channel_id requis'}), 400
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        schedule = await collector.get_optimal_schedule(channel_id)
        return jsonify(schedule)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/thumbnails/analyze', methods=['POST'])
async def analyze_thumbnails():
    """Analyse les miniatures des vidéos les plus performantes."""
    channel_id = request.json.get('channel_id')
    if not channel_id:
        return jsonify({'error': 'channel_id requis'}), 400
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        analysis = await collector.analyze_thumbnails(channel_id)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/live/metrics', methods=['GET'])
async def get_live_metrics():
    """Récupère les métriques en direct d'une chaîne."""
    channel_id = request.args.get('channel_id')
    if not channel_id:
        return jsonify({'error': 'channel_id requis'}), 400
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        metrics = await collector.get_live_metrics(channel_id)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/compare/channels', methods=['POST'])
async def compare_channels():
    """Compare plusieurs chaînes YouTube."""
    channel_ids = request.json.get('channel_ids', [])
    if len(channel_ids) < 2:
        return jsonify({'error': 'Au moins 2 channel_ids requis'}), 400
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        comparison = await collector.compare_channels(channel_ids)
        return jsonify(comparison)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/download/video', methods=['POST'])
async def download_video():
    """Télécharge une vidéo YouTube."""
    video_url = request.json.get('video_url')
    output_path = request.json.get('output_path')
    options = request.json.get('options', {})
    
    if not video_url:
        return jsonify({'error': 'video_url requis'}), 400
        
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        result = await collector.download_video(video_url, output_path, options)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/download/playlist', methods=['POST'])
async def download_playlist():
    """Télécharge une playlist YouTube."""
    playlist_url = request.json.get('playlist_url')
    output_path = request.json.get('output_path')
    options = request.json.get('options', {})
    
    if not playlist_url:
        return jsonify({'error': 'playlist_url requis'}), 400
        
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        result = await collector.download_playlist(playlist_url, output_path, options)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/chapters', methods=['POST'])
async def get_chapters():
    """Récupère les chapitres d'une vidéo YouTube."""
    video_url = request.json.get('video_url')
    
    if not video_url:
        return jsonify({'error': 'video_url requis'}), 400
        
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        chapters = await collector.extract_chapters(video_url)
        return jsonify({'chapters': chapters})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/auto-captions', methods=['POST'])
async def get_auto_captions():
    """Récupère les sous-titres automatiques d'une vidéo YouTube."""
    video_url = request.json.get('video_url')
    
    if not video_url:
        return jsonify({'error': 'video_url requis'}), 400
        
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        captions = await collector.extract_auto_captions(video_url)
        return jsonify({'captions': captions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/convert', methods=['POST'])
async def convert_video():
    """Convertit une vidéo dans un autre format."""
    input_file = request.json.get('input_file')
    output_format = request.json.get('output_format')
    options = request.json.get('options', {})
    
    if not input_file or not output_format:
        return jsonify({'error': 'input_file et output_format requis'}), 400
        
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        result = await collector.convert_video(input_file, output_format, options)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/schedule', methods=['POST'])
async def schedule_download():
    """Programme le téléchargement d'une vidéo."""
    video_url = request.json.get('video_url')
    schedule_time = request.json.get('schedule_time')
    output_path = request.json.get('output_path')
    options = request.json.get('options', {})
    
    if not video_url or not schedule_time:
        return jsonify({'error': 'video_url et schedule_time requis'}), 400
        
    try:
        collector = YouTubeCollector(os.getenv('YOUTUBE_API_KEY'))
        result = await collector.schedule_download(video_url, schedule_time, output_path, options)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

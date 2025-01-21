from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.trend import Trend
from app.models.user import User
from app.services.trend_analyzer import TrendAnalyzer
from app import db

bp = Blueprint('trends', __name__)
trend_analyzer = TrendAnalyzer()

@bp.route('/analyze', methods=['POST'])
@jwt_required()
async def analyze_trends():
    """Analyse les tendances pour les plateformes spécifiées."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    data = request.get_json()
    platforms = data.get('platforms', user.preferred_platforms)
    
    if not platforms:
        return jsonify({'error': 'Aucune plateforme spécifiée'}), 400
    
    try:
        all_trends = []
        for platform in platforms:
            trends = await trend_analyzer.analyze_platform_trends(platform)
            all_trends.extend(trends)
        
        return jsonify({
            'message': 'Analyse des tendances terminée',
            'trends': all_trends
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
@jwt_required()
def get_trend_history():
    """Récupère l'historique des tendances."""
    platform = request.args.get('platform')
    category = request.args.get('category')
    days = int(request.args.get('days', 7))
    
    query = Trend.query
    
    if platform:
        query = query.filter_by(platform=platform)
    if category:
        query = query.filter_by(category=category)
        
    # Limite aux X derniers jours
    from datetime import datetime, timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(Trend.detected_at >= cutoff_date)
    
    trends = query.order_by(Trend.detected_at.desc()).all()
    return jsonify([trend.to_dict() for trend in trends]), 200

@bp.route('/top', methods=['GET'])
@jwt_required()
def get_top_trends():
    """Récupère les tendances les plus performantes."""
    platform = request.args.get('platform')
    limit = int(request.args.get('limit', 10))
    
    query = Trend.query
    
    if platform:
        query = query.filter_by(platform=platform)
    
    # Trie par engagement et limite aux X premiers résultats
    trends = query.order_by(Trend.engagement.desc()).limit(limit).all()
    return jsonify([trend.to_dict() for trend in trends]), 200

@bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_trend_recommendations():
    """Récupère des recommandations de tendances personnalisées."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Filtre les tendances pertinentes pour la niche de l'utilisateur
    trends = Trend.query.filter(
        Trend.category == user.content_niche,
        Trend.platform.in_(user.preferred_platforms)
    ).order_by(
        Trend.engagement.desc()
    ).limit(5).all()
    
    return jsonify({
        'recommendations': [trend.to_dict() for trend in trends],
        'niche': user.content_niche,
        'platforms': user.preferred_platforms
    }), 200

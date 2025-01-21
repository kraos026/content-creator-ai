from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.trend import ContentIdea
from app.models.user import User
from app.services.content_generator import ContentGenerator
from app import db
import os

bp = Blueprint('content', __name__)
content_generator = ContentGenerator(os.environ.get('OPENAI_API_KEY'))

@bp.route('/generate', methods=['POST'])
@jwt_required()
async def generate_content():
    """Génère des idées de contenu basées sur les tendances."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    data = request.get_json()
    trends = data.get('trends', [])
    count = data.get('count', 3)  # Nombre d'idées à générer
    
    if not trends:
        return jsonify({'error': 'Aucune tendance fournie'}), 400
    
    try:
        ideas = await content_generator.generate_content_ideas(
            user_id=current_user_id,
            niche=user.content_niche,
            trends=trends[:count]
        )
        
        return jsonify({
            'message': 'Génération de contenu terminée',
            'ideas': [idea.to_dict() for idea in ideas]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/ideas', methods=['GET'])
@jwt_required()
def get_content_ideas():
    """Récupère les idées de contenu générées."""
    current_user_id = get_jwt_identity()
    
    # Filtres optionnels
    platform = request.args.get('platform')
    used = request.args.get('used', 'false').lower() == 'true'
    
    query = ContentIdea.query.filter_by(user_id=current_user_id)
    
    if platform:
        query = query.filter_by(target_platform=platform)
    query = query.filter_by(is_used=used)
    
    ideas = query.order_by(ContentIdea.generated_at.desc()).all()
    return jsonify([idea.to_dict() for idea in ideas]), 200

@bp.route('/ideas/<int:idea_id>', methods=['PUT'])
@jwt_required()
def update_content_idea(idea_id):
    """Met à jour une idée de contenu."""
    current_user_id = get_jwt_identity()
    idea = ContentIdea.query.filter_by(
        id=idea_id,
        user_id=current_user_id
    ).first()
    
    if not idea:
        return jsonify({'error': 'Idée non trouvée'}), 404
    
    data = request.get_json()
    
    # Champs modifiables
    updateable_fields = [
        'title',
        'description',
        'script',
        'is_used',
        'performance_score'
    ]
    
    for field in updateable_fields:
        if field in data:
            setattr(idea, field, data[field])
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Idée mise à jour avec succès',
            'idea': idea.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/ideas/<int:idea_id>/thumbnail', methods=['POST'])
@jwt_required()
async def regenerate_thumbnail(idea_id):
    """Régénère la miniature pour une idée de contenu."""
    current_user_id = get_jwt_identity()
    idea = ContentIdea.query.filter_by(
        id=idea_id,
        user_id=current_user_id
    ).first()
    
    if not idea:
        return jsonify({'error': 'Idée non trouvée'}), 404
    
    try:
        # Génère une nouvelle miniature
        new_thumbnail_url = await content_generator._generate_thumbnail(
            idea.title,
            idea.target_platform
        )
        
        # Met à jour l'URL de la miniature
        idea.thumbnail_url = new_thumbnail_url
        db.session.commit()
        
        return jsonify({
            'message': 'Miniature régénérée avec succès',
            'thumbnail_url': new_thumbnail_url
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/ideas/<int:idea_id>/script', methods=['POST'])
@jwt_required()
async def regenerate_script(idea_id):
    """Régénère le script pour une idée de contenu."""
    current_user_id = get_jwt_identity()
    idea = ContentIdea.query.filter_by(
        id=idea_id,
        user_id=current_user_id
    ).first()
    
    if not idea:
        return jsonify({'error': 'Idée non trouvée'}), 404
    
    try:
        # Génère un nouveau script
        new_script = await content_generator._generate_script(
            idea.title,
            idea.description,
            idea.target_platform
        )
        
        # Met à jour le script
        idea.script = new_script
        db.session.commit()
        
        return jsonify({
            'message': 'Script régénéré avec succès',
            'script': new_script
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

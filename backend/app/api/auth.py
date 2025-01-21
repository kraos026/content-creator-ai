from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app.models.user import User
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur."""
    data = request.get_json()
    
    # Vérification des champs requis
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'Tous les champs sont requis'}), 400
        
    # Vérification si l'utilisateur existe déjà
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Cet email est déjà utilisé'}), 400
        
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Ce nom d\'utilisateur est déjà pris'}), 400
    
    # Création du nouvel utilisateur
    user = User(
        username=data['username'],
        email=data['email'],
        content_niche=data.get('content_niche'),
        preferred_platforms=data.get('preferred_platforms', []),
        posting_frequency=data.get('posting_frequency')
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Création du token JWT
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Inscription réussie',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur."""
    data = request.get_json()
    
    if not all(k in data for k in ('email', 'password')):
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    return jsonify({'error': 'Email ou mot de passe incorrect'}), 401

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Récupération du profil utilisateur."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
    return jsonify(user.to_dict()), 200

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Mise à jour du profil utilisateur."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    data = request.get_json()
    
    # Mise à jour des champs modifiables
    updateable_fields = [
        'content_niche',
        'preferred_platforms',
        'posting_frequency',
        'username'
    ]
    
    for field in updateable_fields:
        if field in data:
            setattr(user, field, data[field])
    
    # Mise à jour du mot de passe si fourni
    if 'password' in data:
        user.set_password(data['password'])
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profil mis à jour avec succès',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

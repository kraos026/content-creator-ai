from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from app.api.trends import bp as trends_bp
    from app.api.content import bp as content_bp
    from app.api.auth import bp as auth_bp
    
    app.register_blueprint(trends_bp, url_prefix='/api/trends')
    app.register_blueprint(content_bp, url_prefix='/api/content')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}

    return app

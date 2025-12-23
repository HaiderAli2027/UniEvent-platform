from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.models import db
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hackathon.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_ALGORITHM'] = 'HS256'
    
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Register auth routes
        from app.auth import register_auth_routes
        register_auth_routes(app)
        
        # Register event routes
        from app.events import register_events_routes
        register_events_routes(app)
        
        # Register other routes
        from app.routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
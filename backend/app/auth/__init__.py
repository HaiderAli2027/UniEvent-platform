from flask import Blueprint

def register_auth_routes(app):
    """Register authentication routes with the Flask app"""
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

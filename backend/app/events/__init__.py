"""Events module - handles all event-related operations"""

from flask import Blueprint

def register_events_routes(app):
    """Register event routes with the Flask app"""
    from app.events.routes import events_bp
    app.register_blueprint(events_bp)

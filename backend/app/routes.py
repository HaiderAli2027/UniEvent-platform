"""
Main API blueprint hub - aggregates all route blueprints

This file serves as the central registration point for all API blueprints.
Each major feature area (auth, events, interactions) has its own blueprint.
"""

from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

# ============================================================================
# HEALTH CHECK
# ============================================================================

@api_bp.route('/health', methods=['GET'])
def health():
    """API health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Hackathon API is running'}), 200


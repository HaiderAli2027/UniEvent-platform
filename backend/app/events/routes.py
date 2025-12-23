"""
Event Management Routes with Role-Based Access Control (RBAC) + JWT

Permissions:
- CREATE: Societies only
- READ: Everyone (no auth required)
- UPDATE: Society that owns the event
- DELETE: Admin + Society that owns the event
- LIKE/UNLIKE: Logged-in users only
- FILTER: Everyone (by category, society, date range)

IMPORTANT: Specific routes (like /search, /upcoming, /trending) MUST come BEFORE generic routes (/<int:event_id>)
           Otherwise Flask will try to interpret the string as an event ID
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.exceptions import NotFound, Forbidden
from app.models import db, Event, Society, User, user_likes_events
from datetime import datetime, timedelta
from sqlalchemy import or_, and_

events_bp = Blueprint('events', __name__, url_prefix='/api/events')

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_current_user_id():
    """Get current user ID from JWT token"""
    try:
        return get_jwt_identity()
    except:
        return None

def get_current_user_role():
    """Get current user role from JWT claims"""
    try:
        claims = get_jwt()
        return claims.get('role')
    except:
        return None

def get_user_society(user_id):
    """Get user's society if they are a society admin"""
    if not user_id:
        return None
    return Society.query.filter_by(user_id=user_id).first()

def is_admin(role):
    """Check if user is admin"""
    return role == 'admin'

def is_society(role):
    """Check if user is society"""
    return role == 'society'

# ============================================================================
# SEARCH EVENTS (Everyone) - MUST COME BEFORE /<int:event_id>
# ============================================================================

@events_bp.route('/search', methods=['GET'])
def search_events():
    """
    Search events by title/description
    
    Query params:
    - q: Search query (required)
    - category: Filter by category
    - society_id: Filter by society
    """
    try:
        query_param = request.args.get('q', type=str)
        
        if not query_param or len(query_param) < 2:
            return jsonify({'error': 'Search query must be at least 2 characters'}), 400
        
        # Search in title and description
        search_term = f'%{query_param}%'
        query = Event.query.filter(
            Event.is_published == True,
            or_(
                Event.title.ilike(search_term),
                Event.description.ilike(search_term)
            )
        )
        
        # Additional filters
        category = request.args.get('category', type=str)
        if category:
            query = query.filter_by(category=category)
        
        society_id = request.args.get('society_id', type=int)
        if society_id:
            query = query.filter_by(society_id=society_id)
        
        events = query.order_by(Event.event_date.desc()).limit(20).all()
        
        return jsonify({
            'query': query_param,
            'results_count': len(events),
            'data': [e.to_dict(include_organizer=True) for e in events]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# UPCOMING EVENTS (Everyone) - MUST COME BEFORE /<int:event_id>
# ============================================================================

@events_bp.route('/upcoming', methods=['GET'])
def upcoming_events():
    """
    Get upcoming events (next 30 days by default)
    
    Query params:
    - days: Number of days to look ahead (default: 30)
    - limit: Max results (default: 10)
    """
    try:
        days = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Calculate date range
        now = datetime.utcnow()
        future_date = now + timedelta(days=days)
        
        events = Event.query.filter(
            Event.is_published == True,
            Event.event_date >= now,
            Event.event_date <= future_date
        ).order_by(Event.event_date.asc()).limit(limit).all()
        
        return jsonify({
            'days_ahead': days,
            'results_count': len(events),
            'data': [e.to_dict(include_organizer=True) for e in events]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# TRENDING EVENTS (Everyone) - MUST COME BEFORE /<int:event_id>
# ============================================================================

@events_bp.route('/trending', methods=['GET'])
def trending_events():
    """
    Get trending events (sorted by likes)
    
    Query params:
    - limit: Max results (default: 10)
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get events sorted by number of likes (descending)
        events = Event.query.filter_by(is_published=True).all()
        
        # Sort by likes count
        events_with_likes = [(e, e.liked_by.count()) for e in events]
        events_with_likes.sort(key=lambda x: x[1], reverse=True)
        
        trending = [e for e, _ in events_with_likes[:limit]]
        
        return jsonify({
            'results_count': len(trending),
            'data': [e.to_dict(include_organizer=True) for e in trending]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# GET EVENTS BY SOCIETY (Everyone) - MUST COME BEFORE /<int:event_id>
# ============================================================================

@events_bp.route('/society/<int:society_id>', methods=['GET'])
def get_society_events(society_id):
    """Get all events organized by a specific society"""
    try:
        # Verify society exists
        society = Society.query.get_or_404(society_id)
        
        events = Event.query.filter_by(
            society_id=society_id,
            is_published=True
        ).order_by(Event.event_date.desc()).all()
        
        return jsonify({
            'society': society.to_dict(),
            'events_count': len(events),
            'data': [e.to_dict() for e in events]
        }), 200
    
    except NotFound:
        return jsonify({'error': 'Society not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CREATE EVENT (Societies only) - POST /api/events
# ============================================================================

@events_bp.route('', methods=['POST'])
@jwt_required()
def create_event():
    """
    Create a new event (Societies only)
    """
    user_id = get_current_user_id()
    role = get_current_user_role()
    
    # Authorization check
    if not is_society(role):
        return jsonify({'error': 'Only societies can create events'}), 403
    
    # Check if user has a society profile
    society = get_user_society(user_id)
    if not society:
        return jsonify({'error': 'User must have a society profile to create events'}), 400
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'event_date', 'venue']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {", ".join(required_fields)}'}), 400
        
        # Parse event_date
        try:
            event_date = datetime.fromisoformat(data['event_date'])
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DD HH:MM:SS)'}), 400
        
        # Create event
        event = Event(
            society_id=society.id,
            title=data['title'],
            description=data['description'],
            short_description=data.get('short_description'),
            category=data.get('category'),
            event_date=event_date,
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            venue=data['venue'],
            poster=data.get('poster'),
            google_form_link=data.get('google_form_link'),
            is_published=True
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'message': 'Event created successfully',
            'event': event.to_dict(include_organizer=True)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# READ ALL EVENTS (Everyone - with filters) - GET /api/events
# ============================================================================

@events_bp.route('', methods=['GET'])
def list_events():
    """
    Get all events with optional filters
    
    Query params:
    - category: Filter by category
    - society_id: Filter by society
    - page: Pagination (default: 1)
    - per_page: Items per page (default: 10)
    """
    try:
        # Base query - only published events
        query = Event.query.filter_by(is_published=True)
        
        # Filter by category
        category = request.args.get('category', type=str)
        if category:
            query = query.filter_by(category=category)
        
        # Filter by society
        society_id = request.args.get('society_id', type=int)
        if society_id:
            query = query.filter_by(society_id=society_id)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        paginated = query.order_by(Event.event_date.desc()).paginate(
            page=page, 
            per_page=per_page
        )
        
        return jsonify({
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page,
            'data': [e.to_dict(include_organizer=True) for e in paginated.items]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# GET SINGLE EVENT (Everyone) - GET /api/events/<id>
# ============================================================================

@events_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get detailed event information"""
    try:
        event = Event.query.get_or_404(event_id)
        
        return jsonify(event.to_dict(include_organizer=True, include_comments=True)), 200
    
    except NotFound:
        return jsonify({'error': 'Event not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# UPDATE EVENT (Society owner only) - PUT /api/events/<id>
# ============================================================================

@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """
    Update event details (Society owner only)
    """
    user_id = get_current_user_id()
    role = get_current_user_role()
    
    try:
        event = Event.query.get_or_404(event_id)
        
        # Authorization: only society that owns the event can update
        society = get_user_society(user_id)
        if not society or event.society_id != society.id:
            return jsonify({'error': 'Forbidden. Only the society that created this event can update it'}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'short_description' in data:
            event.short_description = data['short_description']
        if 'category' in data:
            event.category = data['category']
        if 'event_date' in data:
            try:
                event.event_date = datetime.fromisoformat(data['event_date'])
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        if 'start_time' in data:
            event.start_time = data['start_time']
        if 'end_time' in data:
            event.end_time = data['end_time']
        if 'venue' in data:
            event.venue = data['venue']
        if 'poster' in data:
            event.poster = data['poster']
        if 'google_form_link' in data:
            event.google_form_link = data['google_form_link']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Event updated successfully',
            'event': event.to_dict(include_organizer=True)
        }), 200
    
    except NotFound:
        return jsonify({'error': 'Event not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# DELETE EVENT (Admin + Society owner) - DELETE /api/events/<id>
# ============================================================================

@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    """
    Delete event (Admin or Society owner only)
    """
    user_id = get_current_user_id()
    role = get_current_user_role()
    
    try:
        event = Event.query.get_or_404(event_id)
        
        # Authorization: admin or society owner can delete
        society = get_user_society(user_id)
        is_owner = society and event.society_id == society.id
        is_admin_user = is_admin(role)
        
        if not (is_admin_user or is_owner):
            return jsonify({'error': 'Forbidden. Only admin or event owner can delete'}), 403
        
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({'message': 'Event deleted successfully'}), 200
    
    except NotFound:
        return jsonify({'error': 'Event not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# LIKE EVENT (Logged-in users only) - POST /api/events/<id>/like
# ============================================================================

@events_bp.route('/<int:event_id>/like', methods=['POST'])
@jwt_required()
def like_event(event_id):
    """
    Like or unlike an event (Logged-in users only)
    """
    user_id = get_current_user_id()
    
    try:
        event = Event.query.get_or_404(event_id)
        user = User.query.get_or_404(user_id)
        
        # Check if user already liked the event
        already_liked = db.session.query(user_likes_events).filter(
            user_likes_events.c.user_id == user_id,
            user_likes_events.c.event_id == event_id
        ).first()
        
        if already_liked:
            # Unlike
            db.session.execute(
                user_likes_events.delete().where(
                    (user_likes_events.c.user_id == user_id) &
                    (user_likes_events.c.event_id == event_id)
                )
            )
            db.session.commit()
            
            return jsonify({
                'message': 'Event unliked',
                'liked': False,
                'total_likes': event.liked_by.count()
            }), 200
        else:
            # Like
            db.session.execute(
                user_likes_events.insert().values(
                    user_id=user_id,
                    event_id=event_id
                )
            )
            db.session.commit()
            
            return jsonify({
                'message': 'Event liked',
                'liked': True,
                'total_likes': event.liked_by.count()
            }), 200
    
    except NotFound:
        return jsonify({'error': 'Event or user not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

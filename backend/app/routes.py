from flask import Blueprint, request, jsonify, send_from_directory
from app.models import db, User, Society, Event, Comment
from datetime import datetime
import os

main = Blueprint('main', __name__)

# Get the frontend directory path
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend')

# Serve HTML pages from frontend folder
@main.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'app.html')
@main.route('/login')
def login_user():
    return send_from_directory(FRONTEND_DIR, 'login-signup.html')

@main.route('/dashboard')
def dashboard():
    return send_from_directory(FRONTEND_DIR, 'dashboard.html')
@main.route('/society-register')
def society_register():
    return send_from_directory(FRONTEND_DIR, 'societyRegForm.html')

@main.route('/app')
def app_page():
    return send_from_directory(FRONTEND_DIR, 'app.html')

@main.route('/join-society')
def join_society():
    return send_from_directory(FRONTEND_DIR, 'join-society.html')

@main.route('/society-form')
def society_form():
    return send_from_directory(FRONTEND_DIR, 'societyRegForm.html')

# Serve CSS files
@main.route('/style/<path:filename>')
def serve_css(filename):
    css_dir = os.path.join(FRONTEND_DIR, 'style')
    return send_from_directory(css_dir, filename)

@main.route('/societyRegForm.html')
def society_reg_form_html():
    return send_from_directory(FRONTEND_DIR, 'societyRegForm.html')
# Serve JS files
@main.route('/script/<path:filename>')
def serve_js(filename):
    js_dir = os.path.join(FRONTEND_DIR, 'script')
    return send_from_directory(js_dir, filename)

# ==================== AUTH ROUTES ====================

# User Registration (Signup)
@main.route('/api/register', methods=['POST'])
def register():
    data = request.form
    try:
        # Check if username already exists
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 400
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data.get('role', 'student')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# User Login
@main.route('/api/login', methods=['POST'])
def login():
    data = request.form
    try:
        # Find user by EMAIL (not username)
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Verify password
        if user.check_password(data['password']):
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict(include_email=True, include_society=True)
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Something went wrong. Please try again.'}), 400

# ==================== SOCIETY ROUTES ====================

# Create Society
@main.route('/api/societies', methods=['POST'])
def create_society():
    data = request.form
    try:
        user_id = data.get('user_id')
        
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user already has a society
        existing_society = Society.query.filter_by(user_id=user_id).first()
        if existing_society:
            return jsonify({'error': 'You already have a registered society'}), 400
        
        # Check if society name already exists
        name_exists = Society.query.filter_by(name=data['name']).first()
        if name_exists:
            return jsonify({'error': 'Society name already taken'}), 400
        
        # Create society
        society = Society(
            user_id=user_id,
            name=data['name'],
            description=data.get('description', ''),
            email=data.get('email', ''),
            whatsapp_number=data.get('whatsapp_number', ''),
            is_verified=False  # Pending approval
        )
        
        # Update user role to society
        user.role = 'society'
        
        db.session.add(society)
        db.session.commit()
        
        return jsonify({
            'message': 'Society registered successfully. Pending admin approval.',
            'society': society.to_dict(),
            'user': user.to_dict(include_email=True, include_society=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Verify Society (Admin only)
@main.route('/api/societies/<int:society_id>/verify', methods=['POST'])
def verify_society(society_id):
    try:
        society = Society.query.get_or_404(society_id)
        society.is_verified = True
        db.session.commit()
        
        return jsonify({
            'message': 'Society verified successfully',
            'society': society.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
# Get All Societies
@main.route('/api/societies', methods=['GET'])
def get_societies():
    societies = Society.query.filter_by(is_active=True).all()
    return jsonify([s.to_dict(include_event_count=True) for s in societies]), 200

# Get Single Society
@main.route('/api/societies/<int:society_id>', methods=['GET'])
def get_society(society_id):
    society = Society.query.get_or_404(society_id)
    return jsonify(society.to_dict(include_owner=True, include_event_count=True)), 200

# ==================== EVENT ROUTES ====================

# Create Event
@main.route('/api/events', methods=['POST'])
def create_event():
    data = request.form
    try:
        event_date_raw = data['event_date']
        # If date is just YYYY-MM-DD, add time so isoformat doesn't crash
        if len(event_date_raw) == 10:
            event_date_raw += "T00:00:00"
        
        event = Event(
            society_id=data['society_id'],
            title=data['title'],
            description=data.get('description', data['title']),
            short_description=data.get('short_description', ''),
            category=data.get('category', ''),
            event_date=datetime.fromisoformat(event_date_raw),
            venue=data.get('venue', ''),
            google_form_link=data.get('google_form_link', '')
            )
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'message': 'Event created successfully',
            'event': event.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Get All Events
@main.route('/api/events', methods=['GET'])
def get_events():
    events = Event.query.filter_by(is_published=True).order_by(Event.event_date.desc()).all()
    return jsonify([e.to_dict(include_organizer=True) for e in events]), 200

# Get Single Event
@main.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.increment_view()
    return jsonify(event.to_dict(include_organizer=True, include_comments=True)), 200

# Like/Unlike Event
@main.route('/api/events/<int:event_id>/like', methods=['POST'])
def like_event(event_id):
    data = request.form
    try:
        user = User.query.get_or_404(data['user_id'])
        event = Event.query.get_or_404(event_id)
        
        if event in user.liked_events:
            user.liked_events.remove(event)
            message = 'Event unliked'
        else:
            user.liked_events.append(event)
            message = 'Event liked'
        
        db.session.commit()
        return jsonify({
            'message': message,
            'likes_count': event.liked_by.count()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ==================== COMMENT ROUTES ====================

# Add Comment
@main.route('/api/events/<int:event_id>/comments', methods=['POST'])
def add_comment(event_id):
    data = request.form
    try:
        comment = Comment(
            user_id=data['user_id'],
            event_id=event_id,
            content=data['content']
        )
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': comment.to_dict(include_author=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Get Comments for Event
@main.route('/api/events/<int:event_id>/comments', methods=['GET'])
def get_comments(event_id):
    comments = Comment.query.filter_by(
        event_id=event_id,
        is_approved=True,
        is_deleted=False
    ).order_by(Comment.created_at.desc()).all()
    
    return jsonify([c.to_dict(include_author=True) for c in comments]), 200
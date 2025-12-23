from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, User, Comment
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/users')

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, None

def sanitize_input(data, allowed_fields):
    """Sanitize user input to only include allowed fields"""
    return {k: v for k, v in data.items() if k in allowed_fields}

# ============================================================================
# USER REGISTRATION
# ============================================================================

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validation
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, error_msg = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Validate username (alphanumeric, 3-80 chars)
        username = data['username'].strip()
        if len(username) < 3 or len(username) > 80:
            return jsonify({'error': 'Username must be between 3 and 80 characters'}), 400
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return jsonify({'error': 'Username can only contain letters, numbers, hyphens, and underscores'}), 400
        
        # Validate role (only allow student and society)
        role = data.get('role', 'student').lower()
        if role not in ['student', 'society']:
            return jsonify({'error': 'Invalid role. Must be either "student" or "society"'}), 400
        
        # Check if username exists
        existing_user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar()
        
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email exists
        existing_email = db.session.execute(
            db.select(User).filter_by(email=data['email'].lower())
        ).scalar()
        
        if existing_email:
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create user
        user = User(
            username=username,
            email=data['email'].lower().strip(),
            first_name=data.get('first_name', '').strip() or None,
            last_name=data.get('last_name', '').strip() or None,
            role=role
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred during registration'}), 500

# ============================================================================
# USER LOGIN
# ============================================================================

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login with JWT token generation"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing username or password'}), 400
        
        # Find user by username
        user = db.session.execute(
            db.select(User).filter_by(username=data['username'])
        ).scalar()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'This account has been deactivated'}), 403
        
        # Create JWT access token with user info
        access_token = create_access_token(
            identity=user.id,  # Store as integer, not string
            additional_claims={
                'role': user.role,
                'username': user.username
            }
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'token_type': 'Bearer',
            'user': user.to_dict(include_email=True, include_society=(user.role == 'society'))
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'An error occurred during login'}), 500

# ============================================================================
# GET CURRENT USER (ME)
# ============================================================================

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current logged-in user's profile"""
    try:
        current_user_id = get_jwt_identity()
        
        user = db.session.get(User, current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(
                include_email=True,
                include_society=(user.role == 'society')
            )
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user profile'}), 500

# ============================================================================
# GET USER PROFILE BY ID
# ============================================================================

@auth_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile details (public endpoint)"""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_active:
            return jsonify({'error': 'User account is inactive'}), 403
        
        # Don't include email for public access
        return jsonify({
            'user': user.to_dict(include_email=False)
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user profile'}), 500

# ============================================================================
# UPDATE USER PROFILE
# ============================================================================

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current user's profile"""
    try:
        current_user_id = get_jwt_identity()
        
        user = db.session.get(User, current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Allowed fields for update
        allowed_fields = ['first_name', 'last_name', 'bio', 'profile_image']
        sanitized_data = sanitize_input(data, allowed_fields)
        
        # Update fields
        for field, value in sanitized_data.items():
            if value is not None:
                # Strip whitespace from string fields
                if isinstance(value, str):
                    value = value.strip()
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict(include_email=True)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500

@auth_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user profile by ID (deprecated - use /me instead)"""
    current_user_id = get_jwt_identity()
    
    # Authorization: Only the owner can update their profile
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized to update this profile'}), 403
    
    # Redirect to update_current_user logic
    return update_current_user()

# ============================================================================
# GET USER'S COMMENTS
# ============================================================================

@auth_bp.route('/<int:user_id>/comments', methods=['GET'])
def get_user_comments(user_id):
    """Get all comments posted by a user"""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # Max 100 per page
        
        # Query comments
        comments_query = db.select(Comment).filter_by(
            user_id=user_id,
            is_deleted=False
        ).order_by(Comment.created_at.desc())
        
        comments = db.session.execute(comments_query).scalars().all()
        
        # Manual pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_comments = comments[start:end]
        
        return jsonify({
            'user': user.username,
            'total_comments': len(comments),
            'page': page,
            'per_page': per_page,
            'comments': [c.to_dict(include_event=True) for c in paginated_comments]
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to fetch comments'}), 500

# ============================================================================
# DELETE USER ACCOUNT
# ============================================================================

@auth_bp.route('/me', methods=['DELETE'])
@jwt_required()
def delete_current_user():
    """Delete current user's account (soft delete)"""
    try:
        current_user_id = get_jwt_identity()
        
        user = db.session.get(User, current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Soft delete
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Account deactivated successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to deactivate account'}), 500

@auth_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user account by ID (deprecated - use /me instead)"""
    current_user_id = get_jwt_identity()
    
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized to delete this account'}), 403
    
    return delete_current_user()

# ============================================================================
# CHANGE PASSWORD
# ============================================================================

@auth_bp.route('/me/password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change current user's password"""
    try:
        current_user_id = get_jwt_identity()
        
        user = db.session.get(User, current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if not data.get('old_password') or not data.get('new_password'):
            return jsonify({'error': 'Missing old_password or new_password'}), 400
        
        # Check old password
        if not user.check_password(data['old_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        is_valid, error_msg = validate_password(data['new_password'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Update password
        user.set_password(data['new_password'])
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password'}), 500
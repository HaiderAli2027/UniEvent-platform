import pytest
import json
from app import create_app
from app.models import db, User, Comment, Event, Society
from datetime import datetime, timedelta

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def sample_user_data():
    """Sample user registration data"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'student'
    }

@pytest.fixture
def sample_society_data():
    """Sample society registration data"""
    return {
        'username': 'testsociety',
        'email': 'society@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'Society',
        'role': 'society'
    }

def register_user(client, user_data):
    """Helper function to register a user"""
    response = client.post('/api/users/register', 
                          data=json.dumps(user_data),
                          content_type='application/json')
    return response

def login_user(client, username, password):
    """Helper function to login and get token"""
    response = client.post('/api/users/login',
                          data=json.dumps({
                              'username': username,
                              'password': password
                          }),
                          content_type='application/json')
    return response

def get_auth_header(token):
    """Helper function to create authorization header"""
    return {'Authorization': f'Bearer {token}'}

# ============================================================================
# REGISTRATION TESTS
# ============================================================================

class TestUserRegistration:
    
    def test_successful_registration(self, client, sample_user_data):
        """Test successful user registration"""
        response = register_user(client, sample_user_data)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User registered successfully'
        assert data['user']['username'] == 'testuser'
        assert data['user']['role'] == 'student'
        assert 'email' not in data['user']  # Email should not be in response
    
    def test_registration_duplicate_username(self, client, sample_user_data):
        """Test registration with duplicate username"""
        # Register first user
        register_user(client, sample_user_data)
        
        # Try to register again with same username
        response = register_user(client, sample_user_data)
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'Username already exists' in data['error']
    
    def test_registration_duplicate_email(self, client, sample_user_data):
        """Test registration with duplicate email"""
        # Register first user
        register_user(client, sample_user_data)
        
        # Try with different username but same email
        sample_user_data['username'] = 'differentuser'
        response = register_user(client, sample_user_data)
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'Email already exists' in data['error']
    
    def test_registration_missing_fields(self, client):
        """Test registration with missing required fields"""
        incomplete_data = {'username': 'testuser'}
        response = register_user(client, incomplete_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required fields' in data['error']
    
    def test_registration_invalid_email(self, client, sample_user_data):
        """Test registration with invalid email format"""
        sample_user_data['email'] = 'invalid-email'
        response = register_user(client, sample_user_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid email format' in data['error']
    
    def test_registration_weak_password(self, client, sample_user_data):
        """Test registration with weak password"""
        sample_user_data['password'] = '12345'  # Too short
        response = register_user(client, sample_user_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'at least 6 characters' in data['error']
    
    def test_registration_invalid_username(self, client, sample_user_data):
        """Test registration with invalid username"""
        sample_user_data['username'] = 'ab'  # Too short
        response = register_user(client, sample_user_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'between 3 and 80 characters' in data['error']
    
    def test_registration_invalid_role(self, client, sample_user_data):
        """Test registration with invalid role"""
        sample_user_data['role'] = 'admin'  # Invalid role
        response = register_user(client, sample_user_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid role' in data['error']
    
    def test_society_registration(self, client, sample_society_data):
        """Test successful society registration"""
        response = register_user(client, sample_society_data)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['user']['role'] == 'society'

# ============================================================================
# LOGIN TESTS
# ============================================================================

class TestUserLogin:
    
    def test_successful_login(self, client, sample_user_data):
        """Test successful user login"""
        # Register user first
        register_user(client, sample_user_data)
        
        # Login
        response = login_user(client, sample_user_data['username'], 
                            sample_user_data['password'])
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Login successful'
        assert 'access_token' in data
        assert data['token_type'] == 'Bearer'
        assert data['user']['username'] == sample_user_data['username']
    
    def test_login_invalid_username(self, client):
        """Test login with non-existent username"""
        response = login_user(client, 'nonexistent', 'password123')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid username or password' in data['error']
    
    def test_login_invalid_password(self, client, sample_user_data):
        """Test login with wrong password"""
        # Register user
        register_user(client, sample_user_data)
        
        # Try login with wrong password
        response = login_user(client, sample_user_data['username'], 
                            'wrongpassword')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid username or password' in data['error']
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post('/api/users/login',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing username or password' in data['error']
    
    def test_login_inactive_user(self, client, app, sample_user_data):
        """Test login with deactivated account"""
        # Register user
        register_user(client, sample_user_data)
        
        # Deactivate user
        with app.app_context():
            user = db.session.execute(
                db.select(User).filter_by(username=sample_user_data['username'])
            ).scalar()
            user.is_active = False
            db.session.commit()
        
        # Try to login
        response = login_user(client, sample_user_data['username'],
                            sample_user_data['password'])
        
        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'deactivated' in data['error']

# ============================================================================
# GET USER PROFILE TESTS
# ============================================================================

class TestGetUserProfile:
    
    def test_get_current_user(self, client, sample_user_data):
        """Test getting current user profile"""
        # Register and login
        register_user(client, sample_user_data)
        login_response = login_user(client, sample_user_data['username'],
                                   sample_user_data['password'])
        token = json.loads(login_response.data)['access_token']
        
        # Get current user
        response = client.get('/api/users/me',
                            headers=get_auth_header(token))
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['username'] == sample_user_data['username']
        assert data['user']['email'] == sample_user_data['email']
    
    def test_get_user_by_id(self, client, app, sample_user_data):
        """Test getting user profile by ID"""
        # Register user
        register_user(client, sample_user_data)
        
        # Get user ID
        with app.app_context():
            user = db.session.execute(
                db.select(User).filter_by(username=sample_user_data['username'])
            ).scalar()
            user_id = user.id
        
        # Get user profile (public access)
        response = client.get(f'/api/users/{user_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['username'] == sample_user_data['username']
        assert 'email' not in data['user']  # Email should not be public
    
    def test_get_nonexistent_user(self, client):
        """Test getting non-existent user"""
        response = client.get('/api/users/9999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'User not found' in data['error']
    
    def test_get_me_without_token(self, client):
        """Test accessing /me without authentication"""
        response = client.get('/api/users/me')
        
        assert response.status_code == 401

# ============================================================================
# UPDATE USER PROFILE TESTS
# ============================================================================

class TestUpdateUserProfile:
    
    def test_update_profile_success(self, client, sample_user_data):
        """Test successful profile update"""
        # Register and login
        register_user(client, sample_user_data)
        login_response = login_user(client, sample_user_data['username'],
                                   sample_user_data['password'])
        token = json.loads(login_response.data)['access_token']
        
        # Update profile
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'This is my bio'
        }
        
        response = client.put('/api/users/me',
                            data=json.dumps(update_data),
                            content_type='application/json',
                            headers=get_auth_header(token))
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Profile updated successfully'
        assert data['user']['first_name'] == 'Updated'
        assert data['user']['bio'] == 'This is my bio'
    
    def test_update_profile_unauthorized(self, client, sample_user_data):
        """Test updating profile without authentication"""
        response = client.put('/api/users/me',
                            data=json.dumps({'bio': 'New bio'}),
                            content_type='application/json')
        
        assert response.status_code == 401
    
    def test_update_profile_no_data(self, client, sample_user_data):
        """Test updating profile with no data"""
        # Register and login
        register_user(client, sample_user_data)
        login_response = login_user(client, sample_user_data['username'],
                                   sample_user_data['password'])
        token = json.loads(login_response.data)['access_token']
        
        response = client.put('/api/users/me',
                            data=json.dumps({}),
                            content_type='application/json',
                            headers=get_auth_header(token))
        
        assert response.status_code == 400

# ============================================================================
# PASSWORD CHANGE TESTS
# ============================================================================

class TestChangePassword:
    
    def test_change_password_success(self, client, sample_user_data):
        """Test successful password change"""
        # Register and login
        register_user(client, sample_user_data)
        login_response = login_user(client, sample_user_data['username'],
                                   sample_user_data['password'])
        token = json.loads(login_response.data)['access_token']
        
        # Change password
        password_data = {
            'old_password': sample_user_data['password'],
            'new_password': 'newpassword123'
        }
        
        response = client.put('/api/users/me/password',
                            data=json.dumps(password_data),
                            content_type='application/json',
                            headers=get_auth_header(token))
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Password changed successfully'
        
        # Verify can login with new password
        login_response = login_user(client, sample_user_data['username'],
                                   'newpassword123')
        assert login_response.status_code == 200
    
    def test_change_password_wrong_old_password(self, client, sample_user_data):
        """Test password change with wrong old password"""
        # Register and login
        register_user(client, sample_user_data)
        login_response = login_user(client, sample_user_data['username'],
                                   sample_user_data['password'])
        token = json.loads(login_response.data)['access_token']
        
        # Try to change with wrong old password
        password_data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }
        
        response = client.put('/api/users/me/password',
                            data=json.dumps(password_data),
                            content_type='application/json',
                            headers=get_auth_header(token))
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'incorrect' in data['error'].lower()
    
    def test_change_password_weak_new_password(self, client, sample_user_data):
        """Test password change with weak new password"""
        # Register and login
        register_user(client, sample_user_data)
        login_response = login_user(client, sample_user_data['username'],
                                   sample_user_data['password'])
        token = json.loads(login_response.data)['access_token']
        
        # Try weak password
        password_data = {
            'old_password': sample_user_data['password'],
            'new_password': '123'  # Too short
        }
        
        response = client.put('/api/users/me/password',
                            data=json.dumps(password_data),
                            content_type='application/json',
                            headers=get_auth_header(token))
        
        assert response.status_code == 400

# ============================================================================
# DELETE USER TESTS
# ============================================================================

class TestDeleteUser:
    
    def test_delete_user_success(self, client, sample_user_data):
        """Test successful account deactivation"""
        # Register and login
        register_user(client, sample_user_data)
        login_response = login_user(client, sample_user_data['username'],
                                   sample_user_data['password'])
        token = json.loads(login_response.data)['access_token']
        
        # Delete account
        response = client.delete('/api/users/me',
                               headers=get_auth_header(token))
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deactivated successfully' in data['message']
        
        # Try to login again - should fail
        login_response = login_user(client, sample_user_data['username'],
                                   sample_user_data['password'])
        assert login_response.status_code == 403

# ============================================================================
# GET USER COMMENTS TESTS
# ============================================================================

class TestGetUserComments:
    
    def test_get_user_comments(self, client, app, sample_user_data):
        """Test getting user's comments"""
        # Register user
        register_user(client, sample_user_data)
        
        with app.app_context():
            user = db.session.execute(
                db.select(User).filter_by(username=sample_user_data['username'])
            ).scalar()
            user_id = user.id
        
        # Get comments
        response = client.get(f'/api/users/{user_id}/comments')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'comments' in data
        assert data['user'] == sample_user_data['username']
    
    def test_get_comments_pagination(self, client, app, sample_user_data):
        """Test comments pagination"""
        # Register user
        register_user(client, sample_user_data)
        
        with app.app_context():
            user = db.session.execute(
                db.select(User).filter_by(username=sample_user_data['username'])
            ).scalar()
            user_id = user.id
        
        # Test with pagination params
        response = client.get(f'/api/users/{user_id}/comments?page=1&per_page=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['page'] == 1
        assert data['per_page'] == 10

# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
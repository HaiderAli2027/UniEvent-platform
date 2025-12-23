import unittest
import json
from datetime import datetime, timedelta
from app import create_app  # Assuming your app factory is in app/__init__.py
from app.models import db, User, Society, Event

class TestEventRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app()
        # Use an in-memory SQLite database for testing to avoid touching production data
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.seed_data()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def seed_data(self):
        """Seed the database with a society user and a student user"""
        # 1. Create a Society Admin User
        soc_user = User(username="tech_society", email="tech@uni.edu", role="society")
        soc_user.set_password("password123")
        
        # 2. Create a Student User
        student = User(username="johndoe", email="john@uni.edu", role="student")
        student.set_password("password123")
        
        db.session.add_all([soc_user, student])
        db.session.commit()

        # 3. Create Society Profile
        soc_profile = Society(user_id=soc_user.id, name="Tech Club", description="Coding club")
        db.session.add(soc_profile)
        db.session.commit()

    def get_token(self, username, password):
        """Helper to login and get JWT token"""
        response = self.client.post('/api/users/login', json={ # Adjust prefix if needed
            "username": username,
            "password": password
        })
        return response.get_json().get('access_token')

    # ============================================================================
    # TEST CASES
    # ============================================================================

    def test_create_event_authorized(self):
        """Test: Society role can successfully create an event"""
        token = self.get_token("tech_society", "password123")
        event_date = (datetime.utcnow() + timedelta(days=5)).isoformat()
        
        payload = {
            "title": "Hackathon 2024",
            "description": "24-hour coding challenge",
            "event_date": event_date,
            "venue": "Main Hall",
            "category": "Technology"
        }

        response = self.client.post('/api/events', 
                                    json=payload,
                                    headers={"Authorization": f"Bearer {token}"})
        
        self.assertEqual(response.status_code, 201)
        self.assertIn("Event created successfully", response.get_json()['message'])

    def test_create_event_unauthorized_role(self):
        """Test: Student role cannot create an event (RBAC check)"""
        token = self.get_token("johndoe", "password123")
        payload = {
            "title": "Illegal Event",
            "description": "Should fail",
            "event_date": datetime.utcnow().isoformat(),
            "venue": "Secret Location"
        }

        response = self.client.post('/api/events', 
                                    json=payload,
                                    headers={"Authorization": f"Bearer {token}"})
        
        self.assertEqual(response.status_code, 403)
        self.assertIn("Only societies can create events", response.get_json()['error'])

    def test_get_upcoming_events(self):
        """Test: Public access to upcoming events list"""
        # First, create an event manually in DB
        with self.app.app_context():
            e = Event(society_id=1, title="Upcoming Party", 
                      description="Test desc", venue="Hall", 
                      event_date=datetime.utcnow() + timedelta(days=1))
            db.session.add(e)
            db.session.commit()

        response = self.client.get('/api/events/upcoming')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data['data']), 0)
        self.assertEqual(data['data'][0]['title'], "Upcoming Party")

    def test_like_unlike_flow(self):
        """Test: Student can like and then unlike an event"""
        # 1. Setup an event
        with self.app.app_context():
            e = Event(society_id=1, title="Liking Event", 
                      description="Test desc", venue="Hall", 
                      event_date=datetime.utcnow() + timedelta(days=1))
            db.session.add(e)
            db.session.commit()
            event_id = e.id

        token = self.get_token("johndoe", "password123")
        
        # 2. Like
        res_like = self.client.post(f'/api/events/{event_id}/like', 
                                    headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_like.status_code, 200)
        self.assertTrue(res_like.get_json()['liked'])
        self.assertEqual(res_like.get_json()['total_likes'], 1)

        # 3. Unlike (Same endpoint)
        res_unlike = self.client.post(f'/api/events/{event_id}/like', 
                                      headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_unlike.status_code, 200)
        self.assertFalse(res_unlike.get_json()['liked'])
        self.assertEqual(res_unlike.get_json()['total_likes'], 0)

    def test_search_events(self):
        """Test: Search functionality with query params"""
        with self.app.app_context():
            e = Event(society_id=1, title="UniqueSearchTerm", 
                      description="Test desc", venue="Hall", 
                      event_date=datetime.utcnow() + timedelta(days=1))
            db.session.add(e)
            db.session.commit()

        response = self.client.get('/api/events/search?q=Unique')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()['data']), 1)

if __name__ == '__main__':
    unittest.main()
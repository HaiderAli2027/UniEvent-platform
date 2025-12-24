from flask import Flask
from flask_cors import CORS
from app.models import db
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hackathon.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Create tables and default admin
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        try:
            from app.models import User
            admin = User.query.filter_by(email='admin@unievent.com').first()
            
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@unievent.com',
                    first_name='Admin',
                    last_name='User',
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✅ Default admin created!")
                print("📧 Email: admin@unievent.com")
                print("🔑 Password: admin123")
            else:
                print("✅ Admin already exists")
        except Exception as e:
            print(f"Note: {e}")
            db.session.rollback()
        
        print("Database ready!")
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app
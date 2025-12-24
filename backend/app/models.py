from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()


# Association table for many-to-many relationship between users and events (likes)
user_likes_events = db.Table(
    'user_likes_events',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False)
)


class User(db.Model):
    __tablename__ = 'users'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False, index=True)
    
    # Profile fields
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(500), nullable=True)
    
    # Status fields
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    society_profile = db.relationship(
        'Society', 
        backref=db.backref('user', lazy=True), 
        uselist=False, 
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    comments = db.relationship(
        'Comment', 
        backref=db.backref('user', lazy=True), 
        lazy='dynamic', 
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    liked_events = db.relationship(
        'Event', 
        secondary=user_likes_events, 
        backref=db.backref('liked_by', lazy='dynamic'),
        lazy='dynamic'
    )
    
    # Composite indexes for common queries
    __table_args__ = (
        db.Index('idx_user_active_role', 'is_active', 'role'),
        db.Index('idx_user_created', 'created_at'),
    )
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set the user password"""
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the user password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_email=False, include_society=False):
        """Convert user object to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_image': self.profile_image,
            'bio': self.bio,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_email:
            data['email'] = self.email
        if include_society and self.society_profile:
            data['society'] = self.society_profile.to_dict(include_owner=False)
        return data


class Society(db.Model):
    __tablename__ = 'societies'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='CASCADE'), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    # Basic information
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(500), nullable=True)
    cover_image = db.Column(db.String(500), nullable=True)
    
    # Contact information
    email = db.Column(db.String(120), nullable=True)
    whatsapp_number = db.Column(db.String(20), nullable=True)
    instagram_handle = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    
    # Status fields
    is_verified = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    member_count = db.Column(db.Integer, default=0, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    events = db.relationship(
        'Event', 
        backref=db.backref('organizer', lazy=True), 
        lazy='dynamic', 
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    # Composite indexes
    __table_args__ = (
        db.Index('idx_society_active_verified', 'is_active', 'is_verified'),
        db.Index('idx_society_created', 'created_at'),
    )
    
    def __repr__(self):
        return f'<Society {self.name}>'
    
    def to_dict(self, include_owner=False, include_event_count=False):
        """Convert society object to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'logo_url': self.logo_url,
            'cover_image': self.cover_image,
            'email': self.email,
            'whatsapp_number': self.whatsapp_number,
            'instagram_handle': self.instagram_handle,
            'website': self.website,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'member_count': self.member_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_owner:
            data['owner'] = self.user.to_dict()
        if include_event_count:
            data['event_count'] = self.events.count()
        return data


class Event(db.Model):
    __tablename__ = 'events'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    society_id = db.Column(
        db.Integer, 
        db.ForeignKey('societies.id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    
    # Event information
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(500), nullable=True)
    
    category = db.Column(db.String(50), nullable=True, index=True)
    
    # Date and time
    event_date = db.Column(db.DateTime, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    
    # Location and media
    venue = db.Column(db.String(300), nullable=True)
    poster = db.Column(db.String(500), nullable=True)
    
    # Registration
    google_form_link = db.Column(db.String(500), nullable=True)
    
    # Status and metrics
    is_published = db.Column(db.Boolean, default=True, nullable=False, index=True)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    comments = db.relationship(
        'Comment', 
        backref=db.backref('event', lazy=True), 
        lazy='dynamic', 
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    # Composite indexes for common queries
    __table_args__ = (
        db.Index('idx_event_published_date', 'is_published', 'event_date'),
        db.Index('idx_event_society_date', 'society_id', 'event_date'),
        db.Index('idx_event_category_date', 'category', 'event_date'),
    )
    
    def __repr__(self):
        return f'<Event {self.title}>'
    
    def is_upcoming(self):
        """Check if event is in the future"""
        return self.event_date > datetime.utcnow()
    
    def increment_view(self):
        """Increment view count"""
        self.view_count += 1
        db.session.commit()
    
    def to_dict(self, include_organizer=False, include_comments=False, include_likes=True):
        """Convert event object to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'short_description': self.short_description,
            'category': self.category,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'venue': self.venue,
            'poster': self.poster,
            'google_form_link': self.google_form_link,
            'is_published': self.is_published,
            'view_count': self.view_count,
            'is_upcoming': self.is_upcoming(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_likes:
            data['likes_count'] = self.liked_by.count()
        
        if include_organizer:
            data['organizer'] = self.organizer.to_dict()
        
        if include_comments:
            approved_comments = self.comments.filter_by(is_approved=True, is_deleted=False)
            data['comments'] = [c.to_dict(include_author=True) for c in approved_comments]
            data['comments_count'] = approved_comments.count()
        
        return data


class Comment(db.Model):
    __tablename__ = 'comments'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    event_id = db.Column(
        db.Integer, 
        db.ForeignKey('events.id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    
    # Content
    content = db.Column(db.Text, nullable=False)
    
    # Status fields
    is_approved = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Composite indexes
    __table_args__ = (
        db.Index('idx_comment_event_approved', 'event_id', 'is_approved', 'is_deleted'),
        db.Index('idx_comment_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f'<Comment {self.id} by User {self.user_id}>'
    
    def soft_delete(self):
        """Soft delete the comment"""
        self.is_deleted = True
        db.session.commit()
    
    def to_dict(self, include_author=False, include_event=False):
        """Convert comment object to dictionary"""
        data = {
            'id': self.id,
            'content': self.content if not self.is_deleted else '[deleted]',
            'is_approved': self.is_approved,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_author and not self.is_deleted:
            data['author'] = self.user.to_dict()
        
        if include_event:
            data['event'] = {
                'id': self.event.id,
                'title': self.event.title
            }
        
        return data
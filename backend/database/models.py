from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Import the shared db instance
from backend.database.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    graduation_year = db.Column(db.String(4))
    degree = db.Column(db.String(100))
    resume = db.Column(db.String(500))
    answers = db.Column(db.JSON)
    job_alerts = db.Column(db.Boolean, default=True)
    auto_apply = db.Column(db.Boolean, default=True)
    linkedin_access_token = db.Column(db.String(500))
    linkedin_profile_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    posted_at = db.Column(db.DateTime)
    source = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title or '',
            'company': self.company or '',
            'location': self.location or '',
            'description': self.description or '',
            'url': self.url or '',
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'source': self.source or '',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Swipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)  # Match UserProfile user_id type
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # 'like' or 'dislike'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FavoriteCompany(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)  # Match UserProfile user_id type
    name = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(500))
    career_page_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Recruiter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    company = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    profile_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)  # Changed to string to match frontend
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    graduation_year = db.Column(db.String(4))
    degree = db.Column(db.String(100))
    resume = db.Column(db.String(500))
    answers = db.Column(db.JSON)
    job_alerts = db.Column(db.Boolean, default=True)
    auto_apply = db.Column(db.Boolean, default=True)
    # LinkedIn fields
    linkedin_access_token = db.Column(db.String(500))
    linkedin_id = db.Column(db.String(100))
    linkedin_name = db.Column(db.String(200))
    linkedin_token_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name or '',
            'email': self.email or '',
            'phone': self.phone or '',
            'graduation_year': self.graduation_year or '',
            'degree': self.degree or '',
            'resume': self.resume or '',
            'answers': self.answers or {},
            'job_alerts': self.job_alerts if self.job_alerts is not None else True,
            'auto_apply': self.auto_apply if self.auto_apply is not None else True,
            'linkedin_connected': bool(self.linkedin_access_token),
            'linkedin_name': self.linkedin_name or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)  # Match UserProfile user_id type
    filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class ApplicationError(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)  # Match UserProfile user_id type
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    error_type = db.Column(db.String(50), nullable=False)  # '404', '405', 'network', etc.
    error_message = db.Column(db.Text)
    job_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LinkedInConnection(db.Model):
    __tablename__ = 'linkedin_connection'
    id = db.Column(db.Integer, primary_key=True)
    linkedin_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)  # Match UserProfile user_id type
    name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200))
    company = db.Column(db.String(200))
    profile_url = db.Column(db.String(500))
    email = db.Column(db.String(200))
    is_alumni = db.Column(db.Boolean, default=False)
    mutual_connections = db.Column(db.Integer, default=0)
    response_rate = db.Column(db.Float, default=0.0)
    last_contact = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('linkedin_id', 'user_id', name='_linkedin_user_uc'),)

class OutreachHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)  # Match UserProfile user_id type
    connection_id = db.Column(db.Integer, db.ForeignKey('linkedin_connection.id'), nullable=False)
    job_title = db.Column(db.String(200))
    company_name = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='sent')  # 'sent', 'delivered', 'read', 'responded'
    response_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
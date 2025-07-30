from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging

# Create a single SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize database with all models"""
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Only seed if completely empty
            if is_database_empty():
                seed_minimal_sample_data()
            else:
                print("📊 Database contains existing data - preserving it")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            logging.error(f"Database initialization failed: {e}")
            raise

def is_database_empty():
    """Check if database is completely empty"""
    try:
        from backend.database.models import UserProfile
        return UserProfile.query.first() is None
    except:
        return True

def seed_minimal_sample_data():
    """Seed only essential data if database is completely empty"""
    try:
        from backend.database.models import UserProfile, Job
        
        print("🌱 Seeding minimal essential data...")
        
        # Create only essential user profile for API connectivity
        sample_profile = UserProfile(
            user_id='test-user',  # Test user ID
            name='Daniel Ajenifuja',
            email='danielajeni.11@gmail.com',
            phone='6479069726',
            graduation_year='2027',
            degree='Western University Computer Science',
            resume='',
            answers={
                'strengths': 'Proficient in Python, React, and cloud technologies',
                'why_company': 'I admire your innovative approach to change lives through technology'
            },
            job_alerts=True,
            auto_apply=True
        )
        db.session.add(sample_profile)
        db.session.commit()
        
        print("✅ Minimal sample data seeded (user profile only)")
        print("   - Jobs will be populated by your job scraper")
        print("   - Favorite companies can be added via the app")
        print("   - LinkedIn connections will be added via OAuth")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error seeding minimal data: {e}")
        logging.error(f"Minimal data seeding failed: {e}")

def reset_db(app):
    """Reset database - DANGER: This will delete all data!"""
    db.init_app(app)
    with app.app_context():
        try:
            db.drop_all()
            print("🗑️  All tables dropped")
            db.create_all()
            print("✅ Database reset successfully")
            seed_minimal_sample_data()
        except Exception as e:
            print(f"❌ Database reset error: {e}")
            raise
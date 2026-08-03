import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', cascade='all, delete-orphan', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    resume_name = db.Column(db.String(255), nullable=False)
    resume_text = db.Column(db.Text, nullable=False)
    job_title = db.Column(db.String(255), nullable=True)
    job_description = db.Column(db.Text, nullable=True)
    
    # Sub-scores and Total ATS Score
    ats_score = db.Column(db.Integer, nullable=False)
    resume_match_score = db.Column(db.Integer, nullable=False)
    skills_score = db.Column(db.Integer, nullable=False)
    keywords_score = db.Column(db.Integer, nullable=False)
    experience_score = db.Column(db.Integer, nullable=False)
    education_score = db.Column(db.Integer, nullable=False)
    formatting_score = db.Column(db.Integer, nullable=False)
    
    # Extracted data and recommendations stored as JSON string
    extracted_data_raw = db.Column(db.Text, nullable=False)  # JSON representation of name, email, phone, education, experience, etc.
    analysis_results_raw = db.Column(db.Text, nullable=False)  # JSON representation of match/missing lists, keywords analysis, guidelines, suggestions
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    @property
    def extracted_data(self):
        try:
            return json.loads(self.extracted_data_raw)
        except Exception:
            return {}
            
    @extracted_data.setter
    def extracted_data(self, value):
        self.extracted_data_raw = json.dumps(value)
        
    @property
    def analysis_results(self):
        try:
            return json.loads(self.analysis_results_raw)
        except Exception:
            return {}
            
    @analysis_results.setter
    def analysis_results(self, value):
        self.analysis_results_raw = json.dumps(value)
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resume_name': self.resume_name,
            'job_title': self.job_title or "General Analysis",
            'ats_score': self.ats_score,
            'resume_match_score': self.resume_match_score,
            'skills_score': self.skills_score,
            'keywords_score': self.keywords_score,
            'experience_score': self.experience_score,
            'education_score': self.education_score,
            'formatting_score': self.formatting_score,
            'extracted_data': self.extracted_data,
            'analysis_results': self.analysis_results,
            'created_at': self.created_at.isoformat()
        }

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("[Database] Database tables initialized successfully.")

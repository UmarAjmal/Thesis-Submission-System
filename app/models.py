from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name field
    gmail = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'author', 'reviewer'
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    author = relationship('Author', uselist=False, back_populates='user')
    reviewer = relationship('Reviewer', uselist=False, back_populates='user')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check the hashed password."""
        return check_password_hash(self.password_hash, password)
    
    def get_reset_token(self, expires_sec=1800):
        """Generate a secure token for password reset."""
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        """Verify the reset token and return the user."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except Exception:
            return None
        return User.query.get(user_id)
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', gmail='{self.gmail}', role='{self.role}')>"

class Author(db.Model):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone_no = db.Column(db.String(20), nullable=True)
    university_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(3), nullable=False)
    
    user = relationship('User', back_populates='author')
    papers = relationship('Paper', back_populates='author', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}', university_name='{self.university_name}')>"

class Reviewer(db.Model):
    __tablename__ = 'reviewers'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    max_papers = db.Column(db.Integer, nullable=False, default=5)
    
    user = relationship('User', back_populates='reviewer')
    assignments = relationship('Assignment', back_populates='reviewer', cascade="all, delete-orphan")
    reviews = relationship('Review', back_populates='reviewer', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Reviewer(id={self.id}, name='{self.name}', qualification='{self.qualification}')>"

class Paper(db.Model):
    __tablename__ = 'papers'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.String(200), nullable=False)
    paper_type = db.Column(db.String(20), nullable=False)  # Choices: 'full', 'short', 'poster'
    file_path = db.Column(db.String(300), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Submitted')  # Choices: 'Submitted', 'Under Review', 'Accepted', 'Rejected'
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    author = relationship('Author', back_populates='papers')
    reviews = relationship('Review', back_populates='paper', cascade="all, delete-orphan")
    assignments = relationship('Assignment', back_populates='paper', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Paper(id={self.id}, title='{self.title}', status='{self.status}')>"

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('reviewers.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Assigned')  # 'Assigned', 'Completed'
    
    paper = relationship('Paper', back_populates='assignments')
    reviewer = relationship('Reviewer', back_populates='assignments')
    review = relationship('Review', back_populates='assignment', uselist=False)
    
    def __repr__(self):
        return f"<Assignment(id={self.id}, paper_id={self.paper_id}, reviewer_id={self.reviewer_id}, status='{self.status}')>"

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('reviewers.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    decision = db.Column(db.String(20), nullable=False)  # 'Accepted' or 'Rejected'
    report = db.Column(db.Text, nullable=False)  # The review report itself
    rejection_reasons = db.Column(db.Text, nullable=True)  # Optional field for rejection reasons
    report_submitted_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    paper = db.relationship('Paper', back_populates='reviews')
    reviewer = db.relationship('Reviewer', back_populates='reviews')
    assignment = db.relationship('Assignment', back_populates='review')

    def __repr__(self):
        return f"<Review(id={self.id}, paper_id={self.paper_id}, reviewer_id={self.reviewer_id}, decision='{self.decision}')>"

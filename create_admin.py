from app import create_app, db
from app.models import User, Author, Reviewer
from werkzeug.security import generate_password_hash
from datetime import datetime

# Initialize the Flask app and set up the app context
app = create_app()
app.app_context().push()

# Admin credentials
admin_email = 'admin@gmail.com'
admin_password = 'admin123'
admin_name = 'Admin'

# Author credentials
author_email = 'author@gmail.com'
author_password = 'author123'
author_name = 'Author'
author_university = 'COMSATS'
author_blood_group = 'A+'

# Reviewer credentials
reviewer_email = 'reviewer@gmail.com'
reviewer_password = 'reviewer123'
reviewer_name = 'Reviewer'
reviewer_university = 'COMSATS'
reviewer_blood_group = 'A+'
reviewer_qualification = 'PhD Computer Science'

# Check if the admin user already exists
existing_admin = User.query.filter_by(gmail=admin_email).first()
if not existing_admin:
    admin_user = User(
        name=admin_name,
        gmail=admin_email,
        password_hash=generate_password_hash(admin_password, method='pbkdf2:sha256'),
        role='admin'
    )
    db.session.add(admin_user)
    db.session.commit()
    print('Admin user created successfully.')
else:
    print('Admin user already exists.')

# Check if the author user already exists
existing_author = User.query.filter_by(gmail=author_email).first()
if not existing_author:
    author_user = User(
        name=author_name,
        gmail=author_email,
        password_hash=generate_password_hash(author_password, method='pbkdf2:sha256'),
        role='author'
    )
    # Add author details (qualification, university, blood group, etc.)
    author = Author(
        user=author_user,  # Linking the user to the author profile
        name=author_name,
        address='N/A',  # Add actual address if needed
        phone_no='N/A',  # Add phone number if needed
        university_name=author_university,
        blood_group=author_blood_group
    )
    db.session.add(author_user)
    db.session.add(author)
    db.session.commit()
    print('Author user created successfully.')
else:
    print('Author user already exists.')

# Check if the reviewer user already exists
existing_reviewer = User.query.filter_by(gmail=reviewer_email).first()
if not existing_reviewer:
    reviewer_user = User(
        name=reviewer_name,
        gmail=reviewer_email,
        password_hash=generate_password_hash(reviewer_password, method='pbkdf2:sha256'),
        role='reviewer'
    )
    # Add reviewer details (qualification, specialization, etc.)
    reviewer = Reviewer(
        user=reviewer_user,  # Linking the user to the reviewer profile
        name=reviewer_name,
        address='N/A',  # Add actual address if needed
        qualification=reviewer_qualification,
        specialization='Software Engineering',  # Add actual specialization if needed
        max_papers=5
    )
    db.session.add(reviewer_user)
    db.session.add(reviewer)
    db.session.commit()
    print('Reviewer user created successfully.')
else:
    print('Reviewer user already exists.')

# Commit changes to the database
db.session.commit()


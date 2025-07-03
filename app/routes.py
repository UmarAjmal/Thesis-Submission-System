from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    send_from_directory,
    abort
)
from flask import send_file
from werkzeug.utils import secure_filename
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from flask_mail import Message
from . import db, mail
from .models import User, Author, Reviewer, Paper, Review, Assignment
from .forms import (
    RegistrationForm,
    LoginForm,
    ThesisSubmissionForm,
    ReviewForm,
    RequestResetForm,
    ResetPasswordForm
)
from .decorators import roles_required
import os
from datetime import datetime

routes = Blueprint('routes', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home Route
@routes.route('/')
def home():
    return render_template('home.html')

# Registration Route
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
      #flash('You are already logged in.', 'info')
        return redirect(url_for('routes.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(gmail=form.gmail.data).first()
        if existing_user:
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('routes.login'))
        
        user = User(
            name=form.name.data,
            gmail=form.gmail.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        if form.role.data == 'author':
            author = Author(
                id=user.id,
                name=form.name.data,
                address=form.address.data,
                phone_no=form.phone_no.data,
                university_name=form.university_name.data,
                blood_group=form.blood_group.data
            )
            db.session.add(author)
        elif form.role.data == 'reviewer':
            reviewer = Reviewer(
                id=user.id,
                name=form.name.data,
                address=form.address.data,
                qualification=form.qualification.data,
                specialization=form.specialization.data,
                max_papers=form.max_papers.data
            )
            db.session.add(reviewer)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('routes.login'))
    
    return render_template('register.html', form=form)

@routes.route('/download/<int:paper_id>')
@login_required
def download_file(paper_id):
    paper = Paper.query.get(paper_id)
    if not paper:
        flash("Paper not found.", 'danger')
        return redirect(url_for('routes.admin_panel'))

    # Assume the file is stored in the 'uploads' folder
    file_path = f'uploads/{secure_filename(paper.file_name)}'
    
    # Send the file as an attachment to download
    return send_file(file_path, as_attachment=True)

# Route for viewing a paper
@routes.route('/view/<int:paper_id>')
@login_required
def view_file(paper_id):
    paper = Paper.query.get(paper_id)
    if not paper:
        flash("Paper not found.", 'danger')
        return redirect(url_for('routes.admin_panel'))

    # Assume the file is stored in the 'uploads' folder
    file_path = f'uploads/{secure_filename(paper.file_name)}'
    
    # Send the file for viewing (not as an attachment)
    return send_file(file_path)


# Manage Submissions Route
@routes.route('/manage_submissions')
@login_required
@roles_required('admin')  # Assuming only admins manage submissions
def manage_submissions():
    # This should retrieve submissions and pass them to the template
    submissions = Paper.query.all()  # Example: Get all papers (you can modify this)
    return render_template('manage_submissions.html', submissions=submissions)


# Login Route
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
       # flash('You are already logged in.', 'info') 
        return redirect(url_for('routes.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(gmail=form.gmail.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
           # flash('Login successful!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.role == 'admin':
                return redirect(url_for('routes.admin_panel'))
            elif user.role == 'author':
                return redirect(url_for('routes.author_panel'))
            elif user.role == 'reviewer':
                return redirect(url_for('routes.reviewer_panel'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html', form=form)

# Logout Route
@routes.route('/logout')
@login_required
def logout():
    logout_user()
   # flash('You have been logged out.', 'info')
    return redirect(url_for('routes.home'))

# Reset Password Route (Request)
@routes.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
     #   flash('You are already logged in.', 'info')
        return redirect(url_for('routes.home'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(gmail=form.gmail.data).first()
        if user:
            send_reset_email(user)
            flash('A password reset link has been sent to your email.', 'success')
            return redirect(url_for('routes.login'))
        else:
            flash('Email address not found.', 'danger')
    
    return render_template('reset_password.html', form=form)

# Reset Password Token Route
@routes.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('routes.home'))
    
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('routes.reset_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('routes.login'))
    
    return render_template('reset_token.html', form=form)

def send_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for('routes.reset_token', token=token, _external=True)
    subject = "Password Reset Request"
    sender = current_app.config['MAIL_DEFAULT_SENDER']
    recipients = [user.gmail]
    body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    msg = Message(subject, sender=sender, recipients=recipients, body=body)
    mail.send(msg)

# Author Panel
@routes.route('/author_panel')
@login_required
@roles_required('author')
def author_panel():
    author = Author.query.get(current_user.id)
    if not author:
        flash('Author profile not found.', 'danger')
        return redirect(url_for('routes.home'))
    
    page = request.args.get('page', 1, type=int)
    papers = Paper.query.filter_by(author_id=author.id).order_by(Paper.upload_date.desc()).paginate(
        page=page,
        per_page=current_app.config.get('ITEMS_PER_PAGE', 10)
    )
    
    return render_template('author_panel.html', papers=papers)

# Submit Thesis
@routes.route('/submit_thesis', methods=['GET', 'POST'])
@login_required
@roles_required('author')
def submit_thesis():
    form = ThesisSubmissionForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(upload_path)
            except RequestEntityTooLarge:
                flash('File is too large. Maximum size allowed is 16MB.', 'danger')
                return redirect(request.url)
            
            keywords = ','.join([k.strip() for k in form.keywords.data.split(',')[:5]])
            paper = Paper(
                title=form.title.data,
                abstract=form.abstract.data,
                keywords=keywords,
                paper_type=form.paper_type.data,
                file_path=filename,  # Store only the filename
                author_id=current_user.id,
                status='Submitted',
                upload_date=datetime.utcnow()
            )
            db.session.add(paper)
            db.session.commit()
            
        #    flash('Thesis submitted successfully!', 'success')
            return redirect(url_for('routes.author_panel'))
        else:
            flash('Invalid file type. Allowed types are PDF and DOCX.', 'danger')
    
    return render_template('submit_thesis.html', form=form)

# View Paper Route
@routes.route('/view_paper/<int:paper_id>', methods=['GET'])
@login_required
def view_paper(paper_id):
    paper = Paper.query.get_or_404(paper_id)
    return render_template('view_paper.html', paper=paper)

# Download Paper Route
@routes.route('/download_paper/<int:paper_id>')
@login_required
def download_paper(paper_id):
    paper = Paper.query.get_or_404(paper_id)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], paper.file_path, as_attachment=True)

# Reviewer Panel
@routes.route('/reviewer_panel')
@login_required
@roles_required('reviewer')
def reviewer_panel():
    reviewer = Reviewer.query.get(current_user.id)
    if not reviewer:
        flash('Reviewer profile not found.', 'danger')
        return redirect(url_for('routes.home'))
    
    page = request.args.get('page', 1, type=int)
    assignments = Assignment.query.filter_by(reviewer_id=reviewer.id).order_by(Assignment.assigned_date.desc()).paginate(
        page=page,
        per_page=current_app.config.get('ITEMS_PER_PAGE', 10)
    )
    
    return render_template('reviewer_panel.html', assignments=assignments)

# Submit Review
@routes.route('/submit_review/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
@roles_required('reviewer')
def submit_review(assignment_id):
    # Fetch the assignment using the assignment_id
    assignment = Assignment.query.get_or_404(assignment_id)

    # Ensure the current user is the assigned reviewer
    if assignment.reviewer_id != current_user.id:
        flash('You do not have permission to access this review.', 'danger')
        return redirect(url_for('routes.reviewer_panel'))

    # Ensure the assignment is not already completed
    if assignment.status != 'Assigned':
        flash('This assignment has already been completed.', 'info')
        return redirect(url_for('routes.reviewer_panel'))

    # Initialize the review form
    form = ReviewForm()

    if form.validate_on_submit():
        try:
            # Prepare rejection reasons if the decision is 'Rejected' or 'Accept with Revision'
            rejection_reasons = form.rejection_reasons.data if form.decision.data in ['Rejected', 'Accept with Revision'] else None

            # Create the review record
            review = Review(
                paper_id=assignment.paper_id,
                reviewer_id=current_user.id,
                assignment_id=assignment.id,
                decision=form.decision.data,
                report=form.report.data,
                rejection_reasons=rejection_reasons,  # Store rejection reasons if applicable
                report_submitted_date=datetime.utcnow()
            )
            db.session.add(review)

            # Update the assignment status to 'Completed'
            assignment.status = 'Completed'

            # Update the paper's status based on the reviewer's decision
            paper = Paper.query.get(assignment.paper_id)
            if form.decision.data == 'Accepted':
                paper.status = 'Accepted'
            elif form.decision.data == 'Rejected':
                paper.status = 'Rejected'
            elif form.decision.data == 'Accept with Revision':
                paper.status = 'Accepted with Revision'
            else:
                flash('Invalid decision status provided.', 'danger')
                return redirect(url_for('routes.reviewer_panel'))

            # Commit the changes to the database
            db.session.commit()

            flash('Review submitted successfully!', 'success')
            return redirect(url_for('routes.reviewer_panel'))

        except Exception as e:
            # If there's an error, roll back and show a flash message
            db.session.rollback()
            print(f"Error during commit: {e}")
            flash('There was an issue submitting the review. Please try again later.', 'danger')
            return redirect(url_for('routes.reviewer_panel'))
    else:
        # If form is not valid, print out form errors for debugging
        print("Form validation failed:", form.errors)
        flash('Please correct the form errors and try again.', 'danger')
        return render_template('submit_review.html', form=form, assignment=assignment)


# Admin Panel
@routes.route('/admin_panel')
@login_required
@roles_required('admin')
def admin_panel():
    page = request.args.get('page', 1, type=int)
    papers = Paper.query.order_by(Paper.upload_date.desc()).paginate(
        page=page,
        per_page=current_app.config.get('ITEMS_PER_PAGE', 10)
    )
    reviewers = Reviewer.query.all()
    return render_template('admin_panel.html', papers=papers, reviewers=reviewers)

# Assign Reviewer Endpoint
@routes.route('/assign_reviewer', methods=['POST'])
@login_required
@roles_required('admin')
def assign_reviewer():
    paper_id = request.form.get('paper_id')
    reviewer_id = request.form.get('reviewer_id')
   
    if not paper_id or not reviewer_id:
        flash('Paper and Reviewer IDs are required.', 'danger')
        return redirect(url_for('routes.admin_panel'))

    paper = Paper.query.get(paper_id)
    reviewer = Reviewer.query.get(reviewer_id)

    if not paper or not reviewer:
        flash('Invalid Paper or Reviewer.', 'danger')
        return redirect(url_for('routes.admin_panel'))

    # Check if the reviewer has reached the maximum number of assignments
    active_assignments = Assignment.query.filter_by(reviewer_id=reviewer.id, status='Assigned').count()
    if active_assignments >= reviewer.max_papers:
        flash(f"Reviewer {reviewer.name} has reached the maximum number of active assignments.", 'warning')
        return redirect(url_for('routes.admin_panel'))

    # Check if the paper is already assigned to this reviewer
    existing_assignment = Assignment.query.filter_by(paper_id=paper.id, reviewer_id=reviewer.id).first()
    if existing_assignment:
        flash('This paper is already assigned to this reviewer.', 'info')
        return redirect(url_for('routes.admin_panel'))

    # Create a new assignment
    assignment = Assignment(
        paper_id=paper.id,
        reviewer_id=reviewer.id,
        assigned_date=datetime.utcnow(),
        status='Assigned'
    )
    db.session.add(assignment)
    db.session.commit()

    flash('Reviewer assigned successfully!', 'success')
    return redirect(url_for('routes.admin_panel'))

# Serve Uploaded Files
@routes.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    paper = Paper.query.filter_by(file_path=filename).first()
    if not paper:
        abort(404)
    
    if current_user.role != 'admin' and paper.author_id != current_user.id:
        flash('You do not have permission to access this file.', 'danger')
        return redirect(url_for('routes.home'))
    
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Error Handlers
@routes.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@routes.app_errorhandler(413)
def request_entity_too_large(e):
    flash('File is too large. Maximum size allowed is 16MB.', 'danger')
    return redirect(request.url), 413

@routes.app_errorhandler(500)
def internal_server_error(e):
    flash('An internal error occurred. Please try again later.', 'danger')
    return render_template('500.html'), 500

@routes.route('/check_users', methods=['GET'])
def check_users():
    """
    Route to display the list of registered users.
    Supports search functionality and pagination.
    """
    # Get search query from request arguments
    search_query = request.args.get('search', '').strip()
    
    # Get current page number from request arguments (default to 1)
    page = request.args.get('page', 1, type=int)
    
    # Query users based on the search query
    if search_query:
        # Filter users by name or email containing the search query (case-insensitive)
        users_query = User.query.filter(
            User.name.ilike(f'%{search_query}%') | User.gmail.ilike(f'%{search_query}%')
        )
    else:
        # If no search query, fetch all users
        users_query = User.query
    
    # Paginate results (e.g., 10 users per page)
    users = users_query.order_by(User.registration_date.desc()).paginate(page=page, per_page=10)
    return render_template('check_users.html', users=users)

@routes.route('/check_status', methods=['GET'])
@login_required
def check_status():
    # Get the papers of the logged-in user
    papers = Paper.query.filter_by(author_id=current_user.id).order_by(Paper.upload_date.desc()).all()
    
    return render_template('check_status.html', papers=papers)

@routes.route('/update_personal_info', methods=['POST'])
@login_required
def update_personal_info():
    # Get the data from the form
    name = request.form.get('name')
    address = request.form.get('address')
    phone_no = request.form.get('phone_no')
    university_name = request.form.get('university_name')
    blood_group = request.form.get('blood_group')

    # Update the current user's information
    current_user.name = name
    current_user.address = address
    current_user.phone_no = phone_no
    current_user.university_name = university_name
    current_user.blood_group = blood_group

    # Commit the changes to the database
    db.session.commit()

    flash('Your personal information has been updated!', 'success')
    return redirect(url_for('routes.author_panel'))  # Redirect to the Author Panel or any other page

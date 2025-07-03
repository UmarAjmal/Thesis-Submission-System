from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    TextAreaField,
    FileField,
    IntegerField,
    BooleanField,
    HiddenField
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    ValidationError,
    Optional,
    NumberRange
)
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.widgets import TextArea
from flask import current_app
from .models import User
from email_validator import validate_email, EmailNotValidError

# Custom validator to check allowed file extensions
def validate_file_extension(form, field):
    if field.data:
        filename = field.data.filename
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'docx'})
        if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            raise ValidationError(f"Invalid file extension. Allowed types are: {', '.join(allowed_extensions)}.")

# Custom Email validator using email_validator
def validate_email_address(form, field):
    """Validates the email address using the email_validator package."""
    try:
        # Validate.
        valid = validate_email(field.data)
        # Update the field data with the normalized form.
        field.data = valid.email
    except EmailNotValidError as e:
        # Raise WTForms ValidationError
        raise ValidationError(str(e))

# Registration Form
class RegistrationForm(FlaskForm):
    role = SelectField(
        'Register as',
        choices=[('author', 'Author/Student'), ('reviewer', 'Reviewer')],
        validators=[DataRequired()]
    )
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(min=2, max=100)]
    )
    address = StringField(
        'Address',
        validators=[DataRequired(), Length(min=5, max=200)]
    )
    phone_no = StringField(
        'Phone Number',
        validators=[Optional(), Length(max=20)]
    )
    qualification = StringField(
        'Qualification',
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Required for Reviewers"}
    )  # Only for reviewers
    university_name = StringField(
        'University Name',
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Required for Authors/Students"}
    )  # Only for authors
    blood_group = StringField(
        'Blood Group',
        validators=[Optional(), Length(max=3)],
        render_kw={"placeholder": "e.g., A+, O- (Required for Authors/Students)"}
    )  # Only for authors
    specialization = StringField(
        'Specialization',
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Required for Reviewers"}
    )  # Only for reviewers
    max_papers = IntegerField(
        'Max Papers to Review',
        default=5,
        validators=[Optional(), NumberRange(min=1, max=20)],
        render_kw={"placeholder": "Required for Reviewers"}
    )  # Only for reviewers
    gmail = StringField(
        'Email',
        validators=[DataRequired(), validate_email_address, Length(max=120)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )
    submit = SubmitField('Register')

    # Custom validators to ensure fields are filled based on role
    def validate_university_name(self, field):
        if self.role.data == 'author' and not field.data:
            raise ValidationError('University Name is required for Authors/Students.')

    def validate_blood_group(self, field):
        if self.role.data == 'author' and not field.data:
            raise ValidationError('Blood Group is required for Authors/Students.')

    def validate_qualification(self, field):
        if self.role.data == 'reviewer' and not field.data:
            raise ValidationError('Qualification is required for Reviewers.')

    def validate_specialization(self, field):
        if self.role.data == 'reviewer' and not field.data:
            raise ValidationError('Specialization is required for Reviewers.')

    def validate_max_papers(self, field):
        if self.role.data == 'reviewer' and field.data is None:
            raise ValidationError('Max Papers to Review is required for Reviewers.')


# Login Form
class LoginForm(FlaskForm):
    gmail = StringField(
        'Email',
        validators=[DataRequired(), validate_email_address, Length(max=120)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


# Thesis Submission Form
class ThesisSubmissionForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[DataRequired(), Length(max=200)]
    )
    abstract = TextAreaField(
        'Abstract',
        validators=[DataRequired()],
        widget=TextArea()
    )
    keywords = StringField(
        'Keywords (comma separated)',
        validators=[DataRequired(), Length(max=200)]
    )
    paper_type = SelectField(
        'Paper Type',
        choices=[('full', 'Full'), ('short', 'Short'), ('poster', 'Poster')],
        validators=[DataRequired()]
    )
    file = FileField(
        'Upload Thesis',
        validators=[
            FileRequired(),
            validate_file_extension
        ],
        render_kw={"accept": ".pdf,.docx"}
    )
    submit = SubmitField('Submit Thesis')


# Review Form
class ReviewForm(FlaskForm):
    decision = SelectField(
        'Decision',
        choices=[
            ('Accepted', 'Accept'),
            ('Rejected', 'Reject'),
            ('Accept with Revision', 'Accept with Revision')
        ],
        validators=[DataRequired()]
    )
    report = TextAreaField(
        'Review Report',
        validators=[DataRequired()],
        widget=TextArea()
    )
    rejection_reasons = TextAreaField(
        'Rejection Reasons',
        validators=[Optional()],
        widget=TextArea(),
        render_kw={"placeholder": "Please provide reasons for rejection (if applicable)"}
    )
    submit = SubmitField('Submit Review')

    def validate_rejection_reasons(self, field):
        """ Ensure rejection reasons are handled based on decision. """
        if self.decision.data == 'Accept with Revision' and not field.data:
            raise ValidationError('Rejection reasons are required when the decision is "Accept with Revision".')
        
        # No validation is needed for rejection reasons when 'Rejected' or 'Accepted' is selected
        if self.decision.data in ['Accepted', 'Rejected'] and field.data:
            raise ValidationError('Rejection reasons should not be provided for "Accepted" or "Rejected".')

    def validate(self, extra_validators=None):
        """
        Custom validation to ensure rejection reasons are handled properly based on the decision.
        """
        # Run base validation
        if not super().validate(extra_validators=extra_validators):
            return False

        # If 'Accept with Revision' is selected, rejection reasons must be filled
        if self.decision.data == 'Accept with Revision' and not self.rejection_reasons.data:
            self.rejection_reasons.errors.append('Rejection reasons are required when the decision is "Accept with Revision".')
            return False

        return True


# Request Password Reset Form
class RequestResetForm(FlaskForm):
    gmail = StringField(
        'Email',
        validators=[DataRequired(), validate_email_address, Length(max=120)]
    )
    submit = SubmitField('Request Password Reset')

    def validate_gmail(self, field):
        user = User.query.filter_by(gmail=field.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


# Reset Password Form
class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'New Password',
        validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )
    submit = SubmitField('Reset Password')


# Assign Reviewer Form
class AssignReviewerForm(FlaskForm):
    paper_id = HiddenField('Paper ID', validators=[DataRequired()])
    reviewer_id = SelectField('Reviewer', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Reviewer')

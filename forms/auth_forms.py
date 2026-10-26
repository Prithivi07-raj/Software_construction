import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models.user import User



class LoginForm(FlaskForm):
    """User authentication form."""

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message="Email is required."),
        ],
        render_kw={
            "placeholder": "you@example.com",
            "autocomplete": "email"
        }
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required.")
        ],
        render_kw={
            "placeholder": "Enter your password",
            "autocomplete": "current-password"
        }
    )

    remember_me = BooleanField('Keep me signed in for 14 days')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """User registration form with strict validation and password strength enforcement."""
    full_name = StringField(
        'Full Name',
        validators=[
            DataRequired(message="Full name is required."),
            Length(min=2, max=100, message="Name must be between 2 and 100 characters.")
        ],
        render_kw={"placeholder": "e.g. Alex Johnson", "autocomplete": "name"}
    )
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Please provide a valid email address."),
            Length(max=120)
        ],
        render_kw={"placeholder": "alex@example.com", "autocomplete": "email"}
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, max=128, message="Password must be at least 8 characters long.")
        ],
        render_kw={"placeholder": "Create a strong password", "autocomplete": "new-password"}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo('password', message="Passwords do not match.")
        ],
        render_kw={"placeholder": "Repeat your password", "autocomplete": "new-password"}
    )
    submit = SubmitField('Create Free Account')

    def validate_email(self, field):
        """Ensure no duplicate accounts with the same email."""
        cleaned_email = field.data.strip().lower()
        if User.query.filter(User.email.ilike(cleaned_email)).first():
            raise ValidationError("An account with this email address already exists.")

    def validate_password(self, field):
        """Enforce basic password complexity requirements."""
        pwd = field.data
        if not re.search(r'[A-Za-z]', pwd) or not re.search(r'\d', pwd):
            raise ValidationError("Password must contain at least one letter and one number.")


class ChangePasswordForm(FlaskForm):
    """Form to securely update account password."""
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired(message="Current password is required.")],
        render_kw={"placeholder": "Enter current password"}
    )
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message="New password is required."),
            Length(min=8, max=128, message="New password must be at least 8 characters.")
        ],
        render_kw={"placeholder": "Enter new secure password"}
    )
    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message="Please confirm your new password."),
            EqualTo('new_password', message="New passwords do not match.")
        ],
        render_kw={"placeholder": "Repeat new password"}
    )
    submit = SubmitField('Update Password')

    def validate_new_password(self, field):
        pwd = field.data
        if not re.search(r'[A-Za-z]', pwd) or not re.search(r'\d', pwd):
            raise ValidationError("Password must contain at least one letter and one number.")

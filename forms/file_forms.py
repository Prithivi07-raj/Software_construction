from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import HiddenField, SubmitField
from wtforms.validators import DataRequired


class FileUploadForm(FlaskForm):
    """File upload form with CSRF validation."""
    file = FileField('Choose File', validators=[FileRequired(message="Please select a file to upload.")])
    submit = SubmitField('Upload')


class DeleteFileForm(FlaskForm):
    """CSRF-protected file deletion form."""
    file_id = HiddenField('File ID', validators=[DataRequired()])
    submit = SubmitField('Delete Permanently')

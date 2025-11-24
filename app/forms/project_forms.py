from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=3, max=200, message='Title must be between 3 and 200 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        Length(max=500, message='Description cannot exceed 500 characters')
    ])
    
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('draft', 'Draft')
    ], default='active')
    
    submit = SubmitField('Save Project')

    def validate_title(self, field):
        """Custom validation example."""
        if "admin" in field.data.lower():
            raise ValidationError("Project title cannot contain 'admin'.")
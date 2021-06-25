from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField,FileField
from wtforms.validators import InputRequired

class SearchForm(FlaskForm):
	search = StringField('search', validators=[InputRequired()])

class DetectionForm(FlaskForm):
	file = FileField('file', validators=[InputRequired()])
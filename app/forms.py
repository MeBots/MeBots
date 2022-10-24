from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Optional, Length, URL
from app.models import User


class BotForm(FlaskForm):
    name = StringField('Bot name', validators=[DataRequired(), Length(max=32)])
    slug = StringField('Shortname', validators=[DataRequired(), Length(max=32)])
    name_customizable = BooleanField('Allow customizing name')
    avatar_url = StringField('Avatar URL', validators=[])
    avatar_url_customizable = BooleanField('Allow customizing avatar')
    callback_url = StringField('Callback URL', validators=[Optional(), Length(max=128), URL()], description='Publicly accessible URL where your bot server can receive message POST requests.')
    description = TextAreaField('Description', validators=[Length(max=1000)])
    prefix = StringField('Command prefix', validators=[Length(max=20)], render_kw={'placeholder': '/, !, #, etc.'})
    prefix_filter = BooleanField('Ignore messages without prefix', validators=[], default=True, description='Prevent receipt of messages that don\'t query your bot. May help save on hosting costs.')
    website = StringField('Website', validators=[Length(max=128)])
    test_group = StringField('Link to join testing/informational group', validators=[Length(max=60)])
    repo = StringField('Source code repository', validators=[Length(max=100)])

    submit = SubmitField('Save')


class InstanceForm(FlaskForm):
    group_id = SelectField('Group')
    name = StringField('Custom name')
    avatar_url = StringField('Custom avatar')

    submit = SubmitField('Add bot')

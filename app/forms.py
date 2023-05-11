from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Optional, Length, URL
from app.models import User


class BotForm(FlaskForm):
    name = StringField('Bot name', validators=[DataRequired()])
    slug = StringField('Shortname', validators=[DataRequired()])
    name_customizable = BooleanField('Allow customizing name')
    avatar_url = StringField('Avatar URL', validators=[])
    avatar_url_customizable = BooleanField('Allow customizing avatar')
    callback_url = StringField('Callback URL', validators=[Optional(), URL()], description='Publicly accessible URL where your bot server can receive message POST requests.')
    description = TextAreaField('Description')
    welcome_message = TextAreaField('Welcome Message', description='This message will be sent when your bot is added to a new server.')
    prefix = StringField('Command prefix', render_kw={'placeholder': '/, !, #, etc.'})
    prefix_filter = BooleanField('Ignore messages without prefix', validators=[], default=True, description='Prevent receipt of messages that don\'t query your bot. May help save on hosting costs.')
    has_user_token_access = BooleanField('Bot needs user token access', validators=[], default=False, description='Does your bot need to act on behalf of the user that adds it? Most bots do not require this. Use of this option is strictly monitored.')
    website = StringField('Website')
    test_group = StringField('Link to join testing/informational group')
    repo = StringField('Source code repository')

    submit = SubmitField('Save')


class InstanceForm(FlaskForm):
    group_id = SelectField('Group')
    name = StringField('Custom name')
    avatar_url = StringField('Custom avatar')
    silence = BooleanField('Silence introduction message?', default=False)

    submit = SubmitField('Add bot')

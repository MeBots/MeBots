from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length, URL
from app.models import User


class BotForm(FlaskForm):
    name = StringField('Bot name', validators=[DataRequired(), Length(max=32)])
    slug = StringField('Shortname', validators=[DataRequired(), Length(max=32)])
    name_customizable = BooleanField('Allow customizing name')
    avatar_url = StringField('Avatar URL', validators=[])
    avatar_url_customizable = BooleanField('Allow customizing avatar')
    callback_url = StringField('Callback URL', validators=[DataRequired(), Length(max=128), URL()])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    website = StringField('Website', validators=[Length(max=128)])
    prefix = StringField('Command prefix', validators=[Length(max=20)])
    test_group = StringField('Link for testing/informational group', validators=[Length(max=60)])
    repo = StringField('GitHub/source code repository', validators=[Length(max=100)])

    submit = SubmitField('Submit')


class InstanceForm(FlaskForm):
    group_id = SelectField('Group')
    name = StringField('Bot name')
    avatar_url = StringField('Bot avatar')

    submit = SubmitField('Add bot')

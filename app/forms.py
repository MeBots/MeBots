from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Bot


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class BotForm(FlaskForm):
    name = StringField('Bot name', validators=[DataRequired()])
    slug = StringField('Shortname', validators=[DataRequired()])
    name_customizable = BooleanField('Allow customizing name')
    avatar_url = StringField('Avatar URL')
    avatar_url_customizable = BooleanField('Allow customizing avatar')
    callback_url = StringField('Callback URL', validators=[DataRequired()])
    description = TextAreaField('Description')

    submit = SubmitField('Submit')


class InstanceForm(FlaskForm):
    group_id = SelectField('Group')
    name = StringField('Bot name')
    avatar_url = StringField('Bot avatar')

    submit = SubmitField('Add bot')

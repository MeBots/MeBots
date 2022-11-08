from flask_login import UserMixin
from app import app, db, login
from app.util import get_now
from app.groupme_api import api_send_message
import os
import binascii



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120))
    avatar = db.Column(db.String(60))
    token = db.Column(db.String(60))

    registered = db.Column(db.Integer)
    last_seen = db.Column(db.Integer)

    bots = db.relationship('Bot', backref='owner', lazy='dynamic')
    instances = db.relationship('Instance', backref='owner', lazy='dynamic')

    def __init__(self, **kwargs):
        for kw, arg in kwargs.items():
            setattr(self, kw, arg)
        self.registered = get_now()

    def avatar_url(self, size='preview'):
        if not self.avatar:
            return '/static/images/unknown.png'
        return app.config['IMAGE_ROOT'] + self.avatar + '.' + size

    def from_json(self, json, token=None):
        self.name = json['name']
        self.email = json['email']
        try:
            self.avatar = json['image_url'][len(app.config['IMAGE_ROOT']):]
        except TypeError:
            print('Missing avatar field.')
            self.avatar = None
        if token is not None:
            self.token = token


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(32))
    name_customizable = db.Column(db.Boolean)
    avatar_url = db.Column(db.String(100))
    avatar_url_customizable = db.Column(db.Boolean)
    callback_url = db.Column(db.String(128))
    description = db.Column(db.String(1000))
    website = db.Column(db.String(128))
    prefix = db.Column(db.String(20))
    prefix_filter = db.Column(db.Boolean, default=True)
    test_group = db.Column(db.String(60))
    repo = db.Column(db.String(100))
    has_user_token_access = db.Column(db.Boolean, default=False)

    token = db.Column(db.String(22))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    instances = db.relationship('Instance', backref='bot', lazy='dynamic')

    created = db.Column(db.Integer)
    updated = db.Column(db.Integer)

    def __init__(self, **kwargs):
        for kw, arg in kwargs.items():
            setattr(self, kw, arg)
        self.created = get_now()

    def json(self):
        return {c.name: getattr(self, c.name) for c in ('slug', 'name',
                                                        'avatar_url')}.update({'instances': len(self.instances.all())})

    def reset_token(self):
        self.token = binascii.b2a_hex(os.urandom(11)).decode()


class Instance(db.Model):
    # This is both the internal primary key and GroupMe's bot_id field.
    id = db.Column(db.String(26), primary_key=True)
    group_id = db.Column(db.String(16))
    group_name = db.Column(db.String(200))

    # These two fields will be nulled if the user cannot or has not made these customizations.
    name = db.Column(db.String(32), nullable=True)
    avatar_url = db.Column(db.String, nullable=True)

    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    created = db.Column(db.Integer)
    updated = db.Column(db.Integer)

    def __init__(self, **kwargs):
        for kw, arg in kwargs.items():
            setattr(self, kw, arg)
        self.created = get_now()

    def send_message(self, text):
        api_send_message(self.bot_id, text)

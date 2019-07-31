from datetime import datetime
from hashlib import md5
from time import time
from flask_login import UserMixin
import jwt
from app import app, db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    # TODO: can we get this from GM?
    #email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    access_token = db.Column(db.String(32))
    # TODO: avatar?

    bots = db.relationship('Bot', backref='owner', lazy='dynamic')
    instances = db.relationship('Instance', backref='owner', lazy='dynamic')

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(32))
    name_customizable = db.Column(db.Boolean)
    avatar_url = db.Column(db.String(70))
    avatar_url_customizable = db.Column(db.Boolean)
    callback_url = db.Column(db.String(128))
    description = db.Column(db.String(200))
    client_id = db.Column(db.String(48))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    instances = db.relationship('Instance', backref='bot', lazy='dynamic')


class Instance(db.Model):
    # This is both the internal primary key and GroupMe's bot_id field.
    id = db.Column(db.String(26), primary_key=True)
    group_id = db.Column(db.String(16))
    group_name = db.Column(db.String(50))

    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

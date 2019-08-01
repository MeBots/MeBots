from datetime import datetime
from hashlib import md5
from time import time
from flask_login import UserMixin
import jwt
from app import app, db, login



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120))
    avatar = db.Column(db.String(45))
    access_token = db.Column(db.String(32))

    bots = db.relationship('Bot', backref='owner', lazy='dynamic')
    instances = db.relationship('Instance', backref='owner', lazy='dynamic')

    def avatar(self, size='preview'):
        return app.config['IMAGE_ROOT'] + self.avatar_url + '.' + size


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(32))
    name_customizable = db.Column(db.Boolean)
    # TODO: store this always as a GroupMe URL string so we don't use up resources with every instance
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

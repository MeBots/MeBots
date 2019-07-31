from datetime import datetime
from hashlib import md5
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import app, db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    bots = db.relationship('Bot', backref='owner', lazy='dynamic')
    instances = db.relationship('Instance', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


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

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.slug)


class Instance(db.Model):
    # This is both the internal primary key and GroupMe's bot_id field.
    id = db.Column(db.String(26), primary_key=True)
    group_id = db.Column(db.String(16))
    group_name = db.Column(db.String(50))
    access_token = db.Column(db.String(32))

    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<{} {} {}>'.format(self.__class__.__name__, self.group_id, self.bot_id)

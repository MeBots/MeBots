from flask_login import UserMixin
from app import app, db, login
import os
import binascii


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120))
    avatar = db.Column(db.String(45))
    token = db.Column(db.String(32))

    bots = db.relationship('Bot', backref='owner', lazy='dynamic')
    instances = db.relationship('Instance', backref='owner', lazy='dynamic')

    def avatar_url(self, size='preview'):
        return app.config['IMAGE_ROOT'] + self.avatar + '.' + size

    def from_json(self, json, token=None):
        self.name = json['name']
        self.email = json['email']
        self.avatar = json['image_url'][len(app.config['IMAGE_ROOT']):]
        if token is not None:
            self.token = token


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
    token = db.Column(db.String(22))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    instances = db.relationship('Instance', backref='bot', lazy='dynamic')

    def json(self):
        return {c.name: getattr(self, c.name) for c in ('slug', 'name',
                                                        'avatar_url')}.update({'instances': len(self.instances.all())})

    def reset_token(self):
        self.token = binascii.b2a_hex(os.urandom(11)).decode()


class Instance(db.Model):
    # This is both the internal primary key and GroupMe's bot_id field.
    id = db.Column(db.String(26), primary_key=True)
    group_id = db.Column(db.String(16))
    group_name = db.Column(db.String(50))

    # These two fields will be nulled if the user cannot or has not made these customizations.
    name = db.Column(db.String(32), nullable=True)
    avatar_url = db.Column(db.String(70), nullable=True)

    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

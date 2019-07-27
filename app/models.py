from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(128))
    bots = db.relationship('Bot', backref='owner', lazy='dynamic')

    def is_authenticated(self):
        return False

    def is_active(self):
        return False

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


class Bot(db.Model):
    __tablename__ = "bots"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(32))
    name_customizable = db.Column(db.Boolean)
    avatar_url = db.Column(db.String(70))
    avatar_url_customizable = db.Column(db.Boolean)
    callback_url = db.Column(db.String(128))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # TODO: store data created and updated?


class BotInstance(db.Model):
    __tablename__ = "bot_instances"
    group_id = db.Column(db.String(16), primary_key=True)
    group_name = db.Column(db.String(50))
    bot_id = db.Column(db.String(26), unique=True)
    owner_id = db.Column(db.String(16))
    owner_name = db.Column(db.String(64))
    access_token = db.Column(db.String(32))

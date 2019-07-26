import os
import requests
from flask import Flask, request, render_template, redirect, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required
from flask_sqlalchemy import SQLAlchemy
import json
import os

from forms import LoginForm


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
# Suppress errors
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(128))

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)


class Bot(db.Model):
    __tablename__ = "bots"
    slug = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(32))
    name_customizable = db.Column(db.Boolean)
    avatar_url = db.Column(db.String(70))
    avatar_url_customizable = db.Column(db.Boolean)
    callback_url = db.Column(db.String(128))

    def __init__(self, name, name_customizable, avatar_url, avatar_url_customizable, callback_url):
        self.name = name
        self.name_customizable = name_customizable
        self.avatar_url = avatar_url
        self.avatar_url_customizable = avatar_url_customizable
        self.callback_url = callback_url


class BotInstance(db.Model):
    __tablename__ = "bot_instances"
    group_id = db.Column(db.String(16), primary_key=True)
    group_name = db.Column(db.String(50))
    bot_id = db.Column(db.String(26), unique=True)
    owner_id = db.Column(db.String(16))
    owner_name = db.Column(db.String(64))
    access_token = db.Column(db.String(32))

    def __init__(self, group_id, group_name, bot_id, owner_id, owner_name, access_token):
        self.group_id = group_id
        self.group_name = group_name
        self.bot_id = bot_id
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.access_token = access_token


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/manager", methods=["GET", "POST"])
def manager():
    access_token = request.args["access_token"]
    callback_url = "https://botagainsthumanitygroupme.herokuapp.com/message"
    me = requests.get(f"https://api.groupme.com/v3/users/me?token={access_token}").json()["response"]
    if request.method == "POST":
        # Build and send bot data
        group_id = request.form["group_id"]
        bot = {
            "name": "Bot Against Humanity",
            "group_id": group_id,
            "avatar_url": "https://i.groupme.com/200x200.png.092e3648ee2745aeb3296a51b3a85e0f",
            "callback_url": callback_url,
        }
        result = requests.post(f"https://api.groupme.com/v3/bots?token={access_token}",
                               json={"bot": bot}).json()["response"]["bot"]
        group = requests.get(f"https://api.groupme.com/v3/groups/{group_id}?token={access_token}").json()["response"]

        # Store in database
        registrant = Bot(group_id, group["name"], result["bot_id"], me["user_id"], me["name"], access_token)
        db.session.add(registrant)
        db.session.commit()
    groups = requests.get(f"https://api.groupme.com/v3/groups?token={access_token}").json()["response"]
    groups = [group for group in groups if not Bot.query.get(group["group_id"])]
    groupme_bots = requests.get(f"https://api.groupme.com/v3/bots?token={access_token}").json()["response"]
    bots = Bot.query.filter_by(owner_id=me["user_id"])
    return render_template("manager.html", access_token=access_token, groups=groups, bots=bots)


@app.route("/delete", methods=["POST"])
def delete_bot():
    data = request.get_json()
    access_token = data["access_token"]
    bot = Bot.query.get(data["group_id"])
    req = requests.post(f"https://api.groupme.com/v3/bots/destroy?token={access_token}", json={"bot_id": bot.bot_id})
    if req.ok:
        db.session.delete(bot)
        db.session.commit()
        return "ok", 200


print("Loaded!")

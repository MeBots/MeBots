from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post
from app.email import send_password_reset_email

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for("root"))
    return render_template('login.html', title='Sign In', form=form)



@app.route("/")
def root():
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

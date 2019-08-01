from datetime import datetime
import requests
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, BotForm, InstanceForm
from app.models import User, Bot, Instance
from app.email import send_password_reset_email


OAUTH_ENDPOINT = 'https://oauth.groupme.com/oauth/authorize?client_id='


def api_get(endpoint, access_token):
    return requests.get('https://api.groupme.com/v3/' + endpoint, params={'token': access_token}).json()['response']


@app.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    bots = Bot.query.paginate(page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('index', page=bots.next_num) if bots.has_next else None
    prev_url = url_for('index', page=bots.prev_num) if bots.has_prev else None
    return render_template('index.html', title='Home',
                           bots=bots.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    access_token = request.args.get('access_token')
    if access_token is None:
        return redirect(OAUTH_ENDPOINT + app.config['CLIENT_ID'])
    me = api_get('users/me', access_token)
    user_id = me.get('user_id')
    if not user_id:
        flash('Invalid user.')
        return redirect(url_for('index'))
    user = User.query.get(user_id)
    if user is None:
        user = User(id=user_id,
                    name=me['name'],
                    email=me['email'],
                    avatar=me['image_url'][len(app.config['IMAGE_ROOT']):],
                    access_token=access_token)
        db.session.add(user)
        db.session.commit()
    login_user(user)
    # TODO: does this actually work? I don't think it would...
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')
    return redirect(next_page)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/user/<user_id>')
def user(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    bots = Bot.query.filter_by(user_id=user.id).paginate(page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('index', page=bots.next_num) if bots.has_next else None
    prev_url = url_for('index', page=bots.prev_num) if bots.has_prev else None
    #bots = user.bots
    return render_template('user.html', user=user, bots=bots.items)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html',
                           title='Edit Profile',
                           form=form)


@app.route('/create_bot', methods=['GET', 'POST'])
@login_required
def create_bot():
    form = BotForm()
    if form.validate_on_submit():
        client_id = form.client_id.data
        bot = Bot(slug=form.slug.data,
                  name=form.name.data,
                  name_customizable=form.name_customizable.data,
                  avatar_url=form.avatar_url.data,
                  avatar_url_customizable=form.avatar_url_customizable.data,
                  callback_url=form.callback_url.data,
                  description=form.description.data,
                  client_id=client_id)
        bot.owner = current_user
        db.session.add(bot)
        db.session.commit()
        flash('Successfully created bot ' + bot.name + '!')
        # TODO: consider a more helpful redirect
        return redirect(url_for('edit_bot', slug=bot.slug))
    return render_template('edit_bot.html',
                           title='Create new bot',
                           form=form)


@app.route('/edit_bot/<slug>', methods=['GET', 'POST'])
@login_required
def edit_bot(slug):
    # TODO: merge with above function
    form = BotForm()
    bot = Bot.query.filter_by(slug=slug).first_or_404()
    if current_user != bot.owner:
        abort(401)
    if form.validate_on_submit():
        bot.slug = form.slug.data
        bot.name = form.name.data
        bot.name_customizable = form.name_customizable.data
        bot.avatar_url = form.avatar_url.data
        bot.avatar_url_customizable = form.avatar_url_customizable.data
        bot.callback_url = form.callback_url.data
        bot.description = form.description.data
        bot.client_id = form.client_id.data
        db.session.commit()
        # TODO; come up with more helpful redirect
        return redirect(url_for('index'))
    # TODO: this repetition feels wrong...
    form.slug.data = bot.slug
    form.name.data = bot.name
    form.name_customizable.data = bot.name_customizable
    form.avatar_url.data = bot.avatar_url
    form.avatar_url_customizable.data = bot.avatar_url_customizable
    form.callback_url.data = bot.callback_url
    form.description.data = bot.description
    form.client_id.data = bot.client_id
    return render_template('edit_bot.html',
                           title='Edit bot',
                           form=form)


@app.route("/manager/<slug>", methods=["GET", "POST"])
def manager(slug):
    bot = Bot.query.filter_by(slug=slug).first_or_404()
    access_token = request.args.get("access_token")
    if access_token is None:
        return redirect(OAUTH_ENDPOINT + bot.client_id)

    me = requests.get(f"https://api.groupme.com/v3/users/me?token={access_token}").json()["response"]
    groups = requests.get(f"https://api.groupme.com/v3/groups?token={access_token}").json()["response"]
    form = InstanceForm()
    form.group_id.choices = [(group["id"], group["name"]) for group in groups]
    if form.validate_on_submit():
        # Build and send instance data
        group_id = form.group_id.data
        bot = {
            "name": form.name.data if bot.name_customizable else bot.name,
            "group_id": group_id,
            "avatar_url": form.avatar_url.data if bot.avatar_url_customizable else bot.avatar_url,
            # TODO: handle callback URLs ourselves!
            "callback_url": bot.callback_url,
        }
        result = requests.post(f"https://api.groupme.com/v3/bots?token={access_token}",
                               json={"bot": bot}).json()["response"]["bot"]
        group = requests.get(f"https://api.groupme.com/v3/groups/{group_id}?token={access_token}").json()["response"]

        # Store in database
        instance = Instance(id=result["bot_id"],
                            group_id=group_id,
                            group_name=group["name"],
                            owner_id=me["user_id"],
                            access_token=access_token)
        db.session.add(instance)
        db.session.commit()
    # TODO: go through instances in database and re-add anything that's not in GroupMe's list
    #groupme_bots = requests.get(f"https://api.groupme.com/v3/bots?token={access_token}").json()["response"]
    instances = [instance for instance in bot.instances if instance.owner_id == me["user_id"]]

    return render_template("manager.html", access_token=access_token, groups=groups, instances=instances, form=form)


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

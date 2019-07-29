from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, BotForm
from app.models import User, Bot, BotInstance
from app.email import send_password_reset_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    bots = Bot.query.paginate(page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('index', page=bots.next_num) if bots.has_next else None
    prev_url = url_for('index', page=bots.prev_num) if bots.has_prev else None
    return render_template('index.html', title='Home',
                           bots=bots.items, next_url=next_url,
                           prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


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


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    bots = user.bots
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
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',
                           title='Edit Profile',
                           form=form)


@app.route('/create_bot', methods=['GET', 'POST'])
@login_required
def create_bot():
    form = BotForm()
    if form.validate_on_submit():
        bot = Bot(slug=form.slug.data,
                  name=form.name.data,
                  name_customizable=form.name_customizable.data,
                  avatar_url=form.avatar_url.data,
                  avatar_url_customizable=form.avatar_url_customizable.data,
                  callback_url=form.callback_url.data)
        db.session.add(bot)
        db.session.commit()
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
    if form.validate_on_submit():
        bot.slug = form.slug.data
        bot.name = form.name.data
        bot.name_customizable = form.name.data
        bot.avatar_url = form.avatar_url.data
        bot.avatar_url_customizable = form.avatar_url_customizable.data
        bot.callback_url = form.callback_url.data
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
    return render_template('edit_bot.html',
                           title='Edit bot',
                           form=form)

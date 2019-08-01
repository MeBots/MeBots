from datetime import datetime
import requests
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import BotForm, InstanceForm
from app.models import User, Bot, Instance


OAUTH_ENDPOINT = 'https://oauth.groupme.com/oauth/authorize?client_id='
API_ROOT = 'https://api.groupme.com/v3/'


def api_get(endpoint, token=None):
    if token is None:
        token = current_user.token
    return requests.get(API_ROOT + endpoint, params={'token': token}).json()['response']

def api_post(endpoint, data={}, token=None):
    if token is None:
        token = current_user.token
    return requests.post(API_ROOT + endpoint,
                         params={'token': token},
                         data=data).json()['response']


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
    token = request.args.get('access_token')
    if token is None:
        return redirect(OAUTH_ENDPOINT + app.config['CLIENT_ID'])
    me = api_get('users/me', token=token)
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
                    token=token)
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
        bot = Bot(slug=form.slug.data,
                  name=form.name.data,
                  name_customizable=form.name_customizable.data,
                  avatar_url=form.avatar_url.data,
                  avatar_url_customizable=form.avatar_url_customizable.data,
                  callback_url=form.callback_url.data,
                  description=form.description.data)
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
    return render_template('edit_bot.html',
                           title='Edit bot',
                           form=form)


@app.route('/manager/<slug>', methods=['GET', 'POST'])
@login_required
def manager(slug):
    bot = Bot.query.filter_by(slug=slug).first_or_404()

    me = api_get('users/me')
    groups = api_get('groups')
    form = InstanceForm()
    form.group_id.choices = [(group['id'], group['name']) for group in groups]
    if form.validate_on_submit():
        # Build and send instance data
        group_id = form.group_id.data
        bot_params = {
            'name': form.name.data if bot.name_customizable else bot.name,
            'group_id': group_id,
            'avatar_url': form.avatar_url.data if bot.avatar_url_customizable else bot.avatar_url,
            # TODO: handle callback URLs ourselves!
            'callback_url': bot.callback_url,
        }
        result = api_post('bots', {'bot': bot_params})['bot']
        group = api_get(f'groups/{group_id}')

        # Store in database
        instance = Instance(id=result['bot_id'],
                            group_id=group_id,
                            group_name=group['name'],
                            owner_id=me['user_id'],
                            bot_id=bot.id)
        db.session.add(instance)
        db.session.commit()
    else:
        form.name.data = bot.name
        form.avatar_url.data = bot.avatar_url
    # TODO: go through instances in database and re-add anything that's not in GroupMe's list
    #groupme_bots = requests.get(f'https://api.groupme.com/v3/bots?token={token}').json()['response']
    instances = [instance for instance in bot.instances if instance.owner_id == me['user_id']]

    return render_template('manager.html', form=form, bot=bot, groups=groups, instances=instances)


@app.route('/delete', methods=['POST'])
def delete_bot():
    data = request.get_json()
    bot = Bot.query.get(data['group_id'])
    req = api_post('bots/destroy', current_user.token, {'bot_id': bot.bot_id})
    if req:
        db.session.delete(bot)
        db.session.commit()
        return 'ok', 200

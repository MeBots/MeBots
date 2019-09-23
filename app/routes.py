import requests
from flask import render_template, flash, redirect, url_for, request, abort, make_response
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


def api_post(endpoint, json={}, token=None, expect_json=True):
    if token is None:
        token = current_user.token
    req = requests.post(API_ROOT + endpoint,
                        params={'token': token},
                        json=json)
    j = req.json()
    print('Response from GroupMe API:')
    print(j)
    return j['response'] if expect_json else req


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    bots = Bot.query.paginate(page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('index', page=bots.next_num) if bots.has_next else None
    prev_url = url_for('index', page=bots.prev_num) if bots.has_prev else None
    return render_template('index.html',
                           bots=bots.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/documentation')
def documentation():
    return render_template('documentation.html')


@app.route('/login')
def login():
    if current_user.is_authenticated:
        next_page = request.cookies.get('next')
        resp = make_response(redirect(next_page or url_for('index')))
        if next_page is not None:
            resp.set_cookie('next', '')
        return resp
    token = request.args.get('access_token')
    print('token: %s' % token)
    if token is None:
        # Store next parameter in cookie to be used after login
        resp = make_response(redirect(OAUTH_ENDPOINT + app.config['CLIENT_ID']))
        next_page = request.args.get('next')
        if next_page:
            resp.set_cookie('next', next_page)
        return resp
    me = api_get('users/me', token=token)
    user_id = me.get('user_id')
    if not user_id:
        flash('Invalid user.')
        return redirect(url_for('index'))
    user = User.query.get(user_id)
    if user is None:
        user = User(id=user_id,
                    token=token)
        user.from_json(me)
        db.session.add(user)
        db.session.commit()
    login_user(user)
    # Check next cookie to see if we need to go anywhere
    return redirect(url_for('index'))


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
    return render_template('user.html', user=user, bots=bots.items, title=user.name)


@app.route('/bot/<slug>')
def bot(slug):
    bot = Bot.query.filter_by(slug=slug).first_or_404()
    return render_template('bot.html', bot=bot, title=bot.name)


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
                  description=form.description.data,
                  website=form.website.data,
                  prefix=form.prefix.data,
                  test_group=form.test_group.data,
                  repo=form.repo.data)
        bot.reset_token()
        bot.owner = current_user
        db.session.add(bot)
        db.session.commit()
        flash('Successfully created bot ' + bot.name + '!')
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
        bot.website = form.website.data
        bot.prefix = form.prefix.data
        bot.test_group = form.test_group.data
        bot.repo = form.repo.data
        db.session.commit()
        return redirect(url_for('bot', slug=bot.slug))
    # TODO: this repetition feels wrong...
    form.slug.data = bot.slug
    form.name.data = bot.name
    form.name_customizable.data = bot.name_customizable
    form.avatar_url.data = bot.avatar_url
    form.avatar_url_customizable.data = bot.avatar_url_customizable
    form.callback_url.data = bot.callback_url
    form.description.data = bot.description
    form.website.data = bot.website
    form.prefix.data = bot.prefix
    form.test_group.data = bot.test_group
    form.repo.data = bot.repo
    return render_template('edit_bot.html',
                           title='Editing ' + bot.name,
                           form=form,
                           token=bot.token,
                           slug=bot.slug)


@app.route('/manager/<slug>', methods=['GET', 'POST'])
@login_required
def manager(slug):
    bot = Bot.query.filter_by(slug=slug).first_or_404()
    me = api_get('users/me')

    groups = api_get('groups')

    # TODO: simplify
    # Dictionary list of the bots that GroupMe has registered with the same callback URL
    groupme_instances = [instance for instance in api_get('bots') if instance['callback_url'] == bot.callback_url]
    # All the instances we have in our database owned by you for this bot
    instances = Instance.query.filter_by(bot_id=bot.id, owner_id=me['user_id']).all()
    # Groups without the bot in them
    groups = [group for group in groups if group['id'] not in [instance.group_id for instance in instances]]
    # Groups that we have a record of a bot for, but for which GroupMe's copy is gone
    missing_instances = [instance for instance in instances if instance.group_id not in
                         [groupme_instance['group_id'] for groupme_instance in groupme_instances]]

    if missing_instances:
        for instance in missing_instances:
            print('Adding back to group ' + instance.group_name)
            bot_params = {
                'name': instance.name or bot.name,
                'group_id': instance.group_id,
                'avatar_url': instance.avatar_url or bot.avatar_url,
                'callback_url': bot.callback_url,
            }
            try:
                result = api_post('bots', {'bot': bot_params})['bot']
                instance.id = result['bot_id']
            except TypeError:
                # Usually an unauthorized error.
                pass
        db.session.commit()
        flash("Missing bots have been restored where possible.")

    form = InstanceForm()
    form.group_id.choices = [(group['id'], group['name']) for group in groups]
    if form.validate_on_submit():
        # Build and send instance data
        group_id = form.group_id.data
        name = form.name.data if bot.name_customizable else bot.name
        name_changed = not (name == bot.name)
        avatar_url = form.avatar_url.data if bot.avatar_url_customizable else bot.avatar_url
        avatar_url_changed = not (avatar_url == bot.avatar_url)
        bot_params = {
            'name': name,
            'group_id': group_id,
            'avatar_url': avatar_url,
            # TODO: handle callback URLs ourselves!
            'callback_url': bot.callback_url,
        }
        result = api_post('bots', {'bot': bot_params})['bot']
        group = api_get(f'groups/{group_id}')

        # Store in database
        instance = Instance(id=result['bot_id'],
                            group_id=group_id,
                            group_name=group['name'],
                            name=name if name_changed else None,
                            avatar_url=avatar_url if avatar_url_changed else None,
                            owner_id=me['user_id'],
                            bot_id=bot.id)
        db.session.add(instance)
        db.session.commit()
    else:
        form.name.data = bot.name
        form.avatar_url.data = bot.avatar_url

    return render_template('manager.html', form=form, bot=bot, groups=groups, instances=instances, title='Add ' + bot.name)


@app.route('/delete', methods=['POST'])
def delete_instance():
    data = request.get_json()
    instance = Instance.query.get(data['instance_id'])
    req = api_post('bots/destroy', {'bot_id': instance.id}, expect_json=False)
    if req.ok:
        db.session.delete(instance)
        db.session.commit()
        return 'ok', 200


@app.route('/reset_token', methods=['POST'])
def reset_token():
    data = request.get_json()
    bot = Bot.query.filter_by(slug=data['slug']).first_or_404()
    if bot is not None:
        bot.reset_token()
        db.session.commit()
        flash('Regenerated token.')
        return '', 200
    return '', 500

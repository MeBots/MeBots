import traceback
from threading import Thread
from flask import render_template, flash, redirect, url_for, request, abort, make_response, send_from_directory, copy_current_request_context
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from sqlalchemy import func, desc
from app import app, db
from app.forms import BotForm, InstanceForm
from app.models import User, Bot, Instance
from app.util import get_now
from app.groupme_api import api_get, api_post, api_create_bot_instance, api_destroy_bot_instance, api_get_all_groups


OAUTH_ENDPOINT = 'https://oauth.groupme.com/oauth/authorize?client_id='


def centralize_bots():
    groupme_bots = api_get('bots')
    instances = current_user.instances
    instance_ids = {instance.id for instance in instances}
    instance_ids_to_instances = {instance.id: instance for instance in instances}
    problematic_bots = [
        bot for bot in groupme_bots
        # Check if each bot instance is in our database and has a non-centralized callback URL
        if bot['bot_id'] in instance_ids and 'https://mebots.io/api/bots/' not in bot['callback_url']
    ]

    for old_bot in problematic_bots:
        print('Will create new bot name={name} in group_id={group_id} to replace old instance {old_bot_id} with callback {callback_url}'.format(
            name=old_bot['name'],
            group_id=old_bot['group_id'],
            old_bot_id=old_bot['bot_id'],
            callback_url=old_bot['callback_url']))
        try:
            instance = instance_ids_to_instances[old_bot['bot_id']]
            bot = Bot.query.get(instance.bot_id)
            # TODO: should use api_create_bot_instance but this is a special case and also very temporary
            bot_params = {
                'name': old_bot['name'],
                'group_id': old_bot['group_id'],
                # This time, let's ignore custom bot IDs since many are broken anyway
                'avatar_url': bot.avatar_url,
                'callback_url': f'https://mebots.io/api/bots/{bot.id}/callback',
            }
            print('Creating new bot instance...')
            result = api_post('bots', {'bot': bot_params})['bot']
            # If we get here, the bot has been created
            print('Creation successful. Destroying old instance ' + old_bot['bot_id'])
            destroy = api_destroy_bot_instance(old_bot['bot_id'])
            print(destroy)

            print('Updating instance record...')
            instance.id = result['bot_id']
            instance.avatar_url = None
            db.session.commit()
            print('Instated new bot instance ID ' + instance.id)
        except Exception as e:
            print('Failed!')
            print(e)
            print(traceback.format_exc())


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = get_now()
        db.session.commit()


@app.route('/')
def index():
    # Temporary! Until everybody is migrated over
    @copy_current_request_context
    def do_centralization():
        centralize_bots()
    if current_user.is_authenticated:
        Thread(target=do_centralization, args=()).start()

    page = request.args.get('page', 1, type=int)
    bots = (db.session.query(Bot)
            .join(Instance)
            .group_by(Bot.id)
            .order_by(desc(func.count(Instance.bot_id)))
            .paginate(page=page, per_page=app.config['ITEMS_PER_PAGE']))
    next_url = url_for('index', page=bots.next_num) if bots.has_next else None
    prev_url = url_for('index', page=bots.prev_num) if bots.has_prev else None
    return render_template('index.html',
                           bots=bots.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login')
def login():
    token = request.args.get('access_token')
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
        # Invalid user
        return redirect(url_for('index'))
    user = User.query.get(user_id)
    if user is None:
        user = User(id=user_id,
                    token=token)
        db.session.add(user)
    user.from_json(me)
    db.session.commit()
    login_user(user)
    # Check next cookie to see if we need to go anywhere
    next_page = request.cookies.get('next')
    if next_page:
        resp = make_response(next_page)
        resp.set_cookie('next', '', expires=0)
        return resp
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/documentation')
def documentation():
    return render_template('documentation.html')


@app.route('/user/<user_id>')
def user(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    bots = Bot.query.filter_by(user_id=user.id).paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'])
    next_url = url_for('index', page=bots.next_num) if bots.has_next else None
    prev_url = url_for('index', page=bots.prev_num) if bots.has_prev else None
    #bots = user.bots
    return render_template('user.html', user=user, bots=bots.items, title=user.name)


@app.route('/bot/<slug>', methods=['GET', 'POST'])
def bot(slug):
    bot = Bot.query.filter_by(slug=slug).first_or_404()

    form = None
    groups = None
    instances = None
    if current_user.is_authenticated:
        me = api_get('users/me')

        legacy_callback_url = bot.callback_url
        callback_url = f'https://mebots.io/api/bots/{bot.id}/callback'

        groups = api_get_all_groups()

        # TODO: simplify
        # Dictionary list of the bots that GroupMe has registered with the same callback URL
        # TODO: stop allowing legacy
        groupme_instances = [instance for instance in api_get('bots') if instance['callback_url'] in (legacy_callback_url, callback_url)]
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
                try:
                    result = api_create_bot_instance(bot, instance.group_id, instance.name, instance.avatar_url)
                    instance.id = result['bot_id']
                except TypeError:
                    # Usually an unauthorized error.
                    pass
            db.session.commit()
            #flash('Missing bots have been restored where possible.')

        form = InstanceForm()
        form.group_id.choices = [(group['id'], group['name']) for group in groups]
        if form.validate_on_submit():
            # Build and send instance data
            group_id = form.group_id.data
            name = form.name.data if bot.name_customizable else bot.name
            name_changed = not (name == bot.name)
            avatar_url = form.avatar_url.data if bot.avatar_url_customizable else bot.avatar_url
            avatar_url_changed = not (avatar_url == bot.avatar_url)
            result = api_create_bot_instance(bot, group_id, name, avatar_url)
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
            # Refresh after creation of bot
            return redirect(url_for('bot', slug=slug))
        else:
            form.name.data = bot.name
            form.avatar_url.data = bot.avatar_url

    return render_template('bot.html', title='Add ' + bot.name,
                           bot=bot, form=form, groups=groups, instances=instances)


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
                  prefix_filter=form.prefix_filter.data,
                  test_group=form.test_group.data,
                  repo=form.repo.data)
        bot.reset_token()
        bot.owner = current_user
        db.session.add(bot)
        db.session.commit()
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
        bot.prefix_filter = form.prefix_filter.data
        bot.test_group = form.test_group.data
        bot.repo = form.repo.data
        bot.updated = get_now()
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
    form.prefix_filter.data = bot.prefix_filter
    form.test_group.data = bot.test_group
    form.repo.data = bot.repo
    return render_template('edit_bot.html',
                           title='Editing ' + bot.name,
                           form=form,
                           bot=bot)


@app.route('/manager/<slug>')
def manager(slug):
    return redirect(url_for('bot', slug=slug))


@app.route('/delete', methods=['POST'])
def delete_instance():
    data = request.get_json()
    instance = Instance.query.get(data['instance_id'])
    req = api_post('bots/destroy', {'bot_id': instance.id}, expect_json=False)
    if req.ok:
        bot = Bot.query.get(instance.bot_id)
        bot.instances.remove(instance)
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


@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

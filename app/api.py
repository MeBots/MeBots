from flask import Blueprint, jsonify, request, g
import requests
from app import db
from app.models import User, Bot, Instance
from app.util import to_json, succ, fail


api_blueprint = Blueprint('api', __name__)


@api_blueprint.errorhandler(404)
def not_found(error):
    return fail('Not found.', 404)


@api_blueprint.errorhandler(401)
def unauthorized(error):
    return fail('You\'re not authorized to perform this action.', 401)


@api_blueprint.errorhandler(403)
def forbidden(error):
    return fail('You don\'t have permission to do this.', 403)


@api_blueprint.errorhandler(405)
def forbidden(error):
    return fail('The method is not allowed for the requested URL.', 405)


@api_blueprint.errorhandler(500)
def internal(error):
    return fail('Internal server error.', 500)


@api_blueprint.route('/bots/<slug>')
# Legacy
@api_blueprint.route('/bot/<slug>')
def api_bot(slug):
    token = request.args.get('token')
    g.bot = Bot.query.filter_by(slug=slug).first_or_404()
    if not token or token != g.bot.token:
        return fail('Missing or invalid token.', 401)
    return g.bot.json()


@api_blueprint.route('/bots/<slug>/instances')
def api_instances(slug):
    g.bot = Bot.query.filter_by(slug=slug).first_or_404()
    instances = g.bot.instances
    json = [{'id': instance.id} for instance in instances]
    return jsonify(json)


@api_blueprint.route('/bots/<slug>/instances/<group_id>')
# Legacy
@api_blueprint.route('/bot/<slug>/instance/<group_id>')
def api_instance(slug, group_id):
    token = request.args.get('token')
    g.bot = Bot.query.filter_by(slug=slug).first_or_404()
    print(token)
    if not token or token != g.bot.token:
        return fail('Missing or invalid token.', 401)
    instance = Instance.query.filter_by(bot_id=g.bot.id, group_id=group_id).first_or_404()
    json = {'id': instance.id}
    if g.bot.has_user_token_access:
        json['token'] = User.query.get(instance.owner_id).token
    return jsonify(json)


# Receiving messages
@api_blueprint.route('/bots/<bot_id>/callback', methods=['POST'])
def api_bot_receive(bot_id):
    g.bot = Bot.query.get_or_404(bot_id)
    print('Received callback for ' + g.bot.name)
    try:
        payload = request.get_json(force=True)
    except Exception:
        return fail('Invalid JSON payload.')
    if not g.bot.prefix_filter or payload['text'].strip().lower().startswith(g.bot.prefix.strip().lower()):
        forward = requests.post(g.bot.callback_url, json=payload)
    return succ('Message processed.', 202)

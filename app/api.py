from flask import Blueprint, jsonify, request, g
from app import db
from app.models import User, Bot, Instance


api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/bots/<slug>')
# Legacy
@api_blueprint.route('/bot/<slug>')
def api_bot(slug):
    token = request.args.get("token")
    g.bot = Bot.query.filter_by(slug=slug).first_or_404()
    if not token or token != g.bot.token:
        return {"error": "Missing or invalid token."}, 401
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
    token = request.args.get("token")
    g.bot = Bot.query.filter_by(slug=slug).first_or_404()
    if not token or token != g.bot.token:
        return {"error": "Missing or invalid token."}, 401
    instance = Instance.query.filter_by(bot_id=g.bot.id, group_id=group_id).first_or_404()
    json = {"id": instance.id}
    if g.bot.has_user_token_access:
        json["token"] = User.query.get(instance.owner_id).token
    return jsonify(json)

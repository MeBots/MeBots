from flask import Blueprint, jsonify, request
from app import db
from app.models import User, Bot, Instance


api_blueprint = Blueprint('api', __name__)


@api_blueprint.before_request
def check_auth():
    token = request.args.get("token")
    if not token or token != bot.token:
        return {"error": "Missing or invalid token."}, 401


@api_blueprint.route('/bot/<slug>')
def api_bot(slug):
    # TODO: use a respectable 404
    bot = Bot.query.filter_by(slug=slug).first_or_404()
    return bot.json()


@api_blueprint.route('/bot/<slug>/instance/<group_id>')
def api_instance(slug, group_id):
    bot = Bot.query.filter_by(slug=slug).first_or_404()
    instance = Instance.query.filter_by(bot_id=bot.id, group_id=group_id).first_or_404()
    json = {"id": instance.id}
    if bot.has_user_token_access:
        json["token"] = User.query.get(instance.owner_id).token
    return jsonify(json)

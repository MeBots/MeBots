from flask import Blueprint, jsonify, request
from app import db
from app.models import Bot, Instance


api_blueprint = Blueprint('api', __name__)

"""
# TODO: actually check token...
@api_blueprint.route('/bot/<slug>')
def bot(slug):
    # TODO: use a respectable 404
    return Bot.query.filter_by(slug=slug).first_or_404().json()
"""


@api_blueprint.route('/bot/<slug>/<group_id>')
def instance_id(slug, group_id):
    token = request.args.get("token")
    bot = Bot.query.filter_by(slug=slug).first_or_404()
    if not token or token != bot.token:
        return {"error": "Missing or invalid token."}
    instance = Instance.query.filter_by(bot_id=bot.id, group_id=group_id).first_or_404()
    return {"instance_id": instance.id}

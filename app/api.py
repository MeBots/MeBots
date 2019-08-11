from flask import Blueprint, jsonify
from app import db
from app.models import Bot, Instance


api_blueprint = Blueprint('api', __name__)


# TODO: actually check token...
@api_blueprint.route('/bot/<slug>')
def bot(slug):
    # TODO: use a respectable 404
    return Bot.query.filter_by(slug=slug).first_or_404().json()

@api_blueprint.route('/bot/<slug>/<group_id>')
def instance_id(slug, group_id):
    bot = Bot.query.filter_by(slug=slug).first_or_404()
    instance = Instance.query.filter_by(bot_id=bot.id, group_id=group_id).first_or_404()
    return instance.id

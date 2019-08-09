from flask import Blueprint, jsonify
from app import db
from app.models import Bot


api_blueprint = Blueprint('api', __name__)


# TODO: actually check token...
@api_blueprint.route('/bot/<slug>')
def bot(slug):
    # TODO: use a respectable 404
    return Bot.query.filter_by(slug=slug).first_or_404().json()

@api_blueprint.route('/bot/<slug>/<group_id>')
def instance_id(slug, group_id):
    bot = Bot.query.filter_by(slug=slug).first_or_404()
    return len(bot.instances.items())

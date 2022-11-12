from app.models import Bot, Instance

slug = input('Bot slug to send warnings for: ')

bot = Bot.query.filter_by(slug=slug).first()
instances = Instance.query.filter_by(bot_id=bot.id, created=None).all()
for instance in instances:
    message = f'Due to a GroupMe update, this bot needs to be reset to keep working. The bot owner, {instance.owner.name}, will need to log in at https://mebots.io/bot/{bot.slug} and it will be automatically regenerated.'
    #instance.send_message(message)
    print(message)


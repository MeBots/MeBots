from app.models import Bot, Instance
import argparse

argument_parser = ArgumentParser

bot_id = int(input('Bot ID to send warnings for: '))

bot = Bot.query.filter_by(slug=slug)
instances = Instance.query.filter_by(bot_id=bot.id, created=None).all()
for instance in instances:
    message = f'Due to a GroupMe update, this bot needs to be reset to continue working. The bot owner, {instance.owner.name}, will need to log in at https://mebots.io/bot/{bot.slug} and the bot will be automatically regenerated. Thanks!'
    print(message)



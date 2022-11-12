from app.models import Bot, Instance

bot = Bot.query.filter(Bot.slug.in_(slugs).first()
instances = Instance.query.filter_by(bot_id=bot.id, created=None).all()
groups = {}
for instance in instances:
    if instance.owner not in groups:
        groups[instance.owner] = []
    groups[email].append(instance.group_name)
    #message = f'> Due to a GroupMe update, this bot needs to be reset to keep working. The bot owner, {instance.owner.name}, will need to log in at https://mebots.io/bot/{bot.slug} and it will be automatically repaired.'
    #instance.send_message(message)

for user, group_names in groups.items():
    name = user.split()[0]
    groups_phrase = group_names.join('
    message = f'Hello {name}!\n\nDue to a GroupMe update, some your bots from MeBots in some of your groups, including  need to be reset to keep working. This includes

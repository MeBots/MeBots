from app.models import Bot, Instance

instances = Instance.query.filter_by(created=None).all()
groups = {}
for instance in instances:
    """
    if instance.owner not in groups:
        groups[instance.owner] = []
    groups[instance.owner.email].append(instance.group_name)
    """
    print()
    email = instance.owner.email
    if not email:
        print('Skipping instance with unknown owner.')
        continue
    print(f'{instance.bot.name} in group {instance.group_name} owned by {email}')
    message = f'Due to a recent GroupMe update, this bot needs to be reset to keep working. The bot owner, {instance.owner.name}, will need to log in at https://mebots.io/bot/{instance.bot.slug} and all bots disabled by the update will be automatically restored. We apologize for the inconvenience, and thank you for your help!'
    print(message)
    instance.send_message(message)
"""
instances = Instance.query.filter_by(created=None).all()
users = set()
groups = {}
bots = {}
for instance in instances:
    if instance.owner not in users:
        users.add(instance.owner)
        groups[instance.owner] = set()
        bots[instance.owner] = set()
    groups[instance.owner].add(instance.group_name)
    bots[instance.owner].add(instance.bot.name)


def list_to_phrase(items):
    item_count = len(items)
    last_item = items.pop()
    phrase = ', '.join(items)
    if item_count > 2:
        phrase += ', '
    if item_count == 2:
        phrase += ' '
    if item_count > 1:
        phrase += 'and '
    phrase += last_item
    return phrase


for user in users:
    if not user.email:
        continue
    try:
        name = user.name.split()[0]
    except AttributeError:
        name = 'MeBots user'
    user_groups = groups[user]
    user_bots = bots[user]
    print(user.email)
    message = f'Hello {name}!\n\nDue to a GroupMe update, some your MeBots bots (including {list_to_phrase(user_bots)}), need to be reset to keep working. This includes bots in the group(s) {list_to_phrase(user_groups)}.\n\nIf you log into MeBots, these bots will automatically be repaired with no further action required.'
    print(message)
    print()
"""

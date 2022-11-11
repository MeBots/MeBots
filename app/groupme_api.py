import requests
from flask_login import current_user


API_ROOT = 'https://api.groupme.com/v3/'
PAGE_SIZE = 500


def api_get(endpoint, token=None, params={}):
    if token is None:
        token = current_user.token
    j = requests.get(API_ROOT + endpoint, params={'token': token, **params}).json()
    response = j.get('response')
    if response is None:
        print('Error response from GroupMe API:')
        print(j)
        return None
    return response


def api_post(endpoint, json={}, token=None, expect_json=True):
    if token is None:
        token = current_user.token
    req = requests.post(API_ROOT + endpoint,
                        params={'token': token},
                        json=json)
    if expect_json:
        j = req.json()
        print('Response from GroupMe API:')
        print(j)
        return j['response']
    return req


def api_send_message(bot_id, text):
    url = API_ROOT + 'bots/post'
    message = {
        'bot_id': bot_id,
        'text': text,
    }
    print('Sending message:')
    print(message)
    r = requests.post(url, json=message)
    print('Response from GroupMe API:')
    print(r.json())


def api_create_bot_instance(bot, group_id, name=None, avatar_url=None, token=None):
    bot_params = {
        'name': name or bot.name,
        'group_id': group_id,
        'avatar_url': avatar_url or bot.avatar_url,
        'callback_url': f'https://mebots.io/api/bots/{bot.id}/callback',
    }
    return api_post('bots', {'bot': bot_params}, token=token)['bot']


def api_destroy_bot_instance(bot_id, token=None):
    return api_post('bots/destroy', {'bot_id': bot_id}, expect_json=False, token=token)


def api_get_all_groups():
    groups = []
    page = 1
    while True:
        groups_page = api_get('groups', params={
            'page': page,
            'per_page': PAGE_SIZE,
            'omit': 'memberships',
        })
        groups += groups_page
        if len(groups_page) < PAGE_SIZE:
            break
        page += 1
    return groups

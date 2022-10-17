import requests
from flask_login import current_user


API_ROOT = 'https://api.groupme.com/v3/'


def api_get(endpoint, token=None, params={}):
    if token is None:
        token = current_user.token
    j = requests.get(API_ROOT + endpoint, params={'token': token, **params}).json()
    response = j.get('response')
    if response is None:
        print('Error response from GroupMe API:')
        print(j)
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


def api_create_bot_instance(bot, group_id, name=None, avatar_url=None):
    bot_params = {
        'name': name or bot.name,
        'group_id': group_id,
        'avatar_url': avatar_url or bot.avatar_url,
        'callback_url': f'https://mebots.io/api/bots/{bot.id}/callback',
    }
    return api_post('bots', {'bot': bot_params})['bot']


def api_destroy_bot_instance(bot_id):
    return api_post('bots/destroy', {'bot_id': bot_id}, expect_json=False)


import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Override this in production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLIENT_ID = 'ZdSzatBHBT06cjk100Bvk4RHuPCyKy53FQFpnnnHZFbPu9lB'
    ITEMS_PER_PAGE = 16
    IMAGE_ROOT = 'https://i.groupme.com/'

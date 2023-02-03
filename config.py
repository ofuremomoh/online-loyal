import os

BASE_DIR = os.path.abspath(os.path.dirname(__name__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this-is-less-secure'

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:CoreSocial94!@localhost:5433/online-loyal"
    #SQLALCHEMY_DATABASE_URI = "postgresql://bbxgopmswhnpgl:6efff7ccd98af286e666c018d5dbd8eea7b1ed0538856df9c9abaa57bbdf8e43@ec2-34-225-159-178.compute-1.amazonaws.com:5432/d4kn3aeevrqehk"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 25
    FOLLOWED_PER_PAGE = 5
    FOLLOWERS_PER_PAGE = 5
    #PORT = int(os.environ.get("PORT"))
    # mail config
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    FLASKER= 'theofuremomoh@outlook.com,momohofure@gmail.com, info.starturn@gmail.com, phurell1@mailto.plus '
    # pusher config
    PUSHER_APP_ID = os.environ.get('PUSHER_APP_ID')
    PUSHER_KEY = os.environ.get('PUSHER_KEY')
    PUSHER_SECRET = os.environ.get('PUSHER_SECRET')
    PUSHER_CLUSTER = os.environ.get('PUSHER_CLUSTER')
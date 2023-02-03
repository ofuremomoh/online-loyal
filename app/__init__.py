from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import Config


from flask_bootstrap import Bootstrap

bootstrap = Bootstrap()

# extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
moment = Moment()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    app.app_context().push()
    db.init_app(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:CoreSocial94!@localhost:5433/online-loyal"
    #app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://bbxgopmswhnpgl:6efff7ccd98af286e666c018d5dbd8eea7b1ed0538856df9c9abaa57bbdf8e43@ec2-34-225-159-178.compute-1.amazonaws.com:5432/d4kn3aeevrqehk"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'info.starturn@gmail.com'
    app.config['MAIL_PASSWORD'] = 'CoreSocial94!'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SECRET_KEY'] = 'SECRET_KEY'
    app.config['FLASKER'] = 'theofuremomoh@outlook.com,momohofure@gmail.com, info.starturn@gmail.com, phurell1@mailto.plus '
    app.config['PRODUCTS_PER_PAGE'] = 4
    app.config['CARTS_PER_PAGE'] = 7
    app.config['ORDERS_PER_PAGE'] = 5
    app.config['SECURITY_PASSWORD_SALT'] = 'loevr'
    
    migrate.init_app(app, db)
    login.init_app(app)

    moment.init_app(app)
    bootstrap.init_app(app)



    from app.main import bp as main_bp
    app.register_blueprint(main_bp)




    return app

from app import models
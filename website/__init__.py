from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_mail import Mail

import os

db = SQLAlchemy()
mail = Mail()


def create_app():
    from website.views import views
    from website.models import models
    from website.dis import dis
    from website.auth import auth
    from website.errors import errors
    from website.exam import exam
    from website.api import api

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mypass@myip/nepalvac_site'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    app.config['TRAP_HTTP_EXCEPTIONS']=True
    app.config['MAIL_SERVER'] = 'mail.nepalvacc.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'no-reply@nepalvacc.com'
    app.config['MAIL_PASSWORD'] = 'mypass'
    app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@nepalvacc.com'
    app.config['MAIL_MAX_EMAILS'] = 1
    app.config['MAIL_ASCII_ATTACHMENTS'] = False
    app.secret_key = b"mykey"
    app.permanent_session_lifetime = timedelta(days=1234)

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'false'
    db.init_app(app)
    mail.init_app(app)

    app.register_blueprint(models)
    app.register_blueprint(views, url_prefix="/dashboard")
    app.register_blueprint(dis, url_prefix="/dashboard")
    app.register_blueprint(auth, url_prefix="/vatsim")
    app.register_blueprint(errors)
    app.register_blueprint(exam, name="exam questions")
    app.register_blueprint(api, url_prefix="/api")

    return app

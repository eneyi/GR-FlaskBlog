from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_mdeditor import MDEditor
from flaskext.markdown import Markdown
from flask_sitemap import Sitemap

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "SECRET KEY"

    from goodrobots.blueprints.views import views
    from goodrobots.blueprints.auth import auth
    from goodrobots.blueprints.errors import errors
    from goodrobots.blueprints.editor import editor

    app.register_blueprint(views)
    app.register_blueprint(auth)
    app.register_blueprint(errors)
    app.register_blueprint(editor)

    app.config['MDEDITOR_FILE_UPLOADER'] = "/static/assets/img/posts/pimgs"
    app.config['MDEDITOR_LANGUAGE']  = 'en'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['MAIL_SERVER'] = 'MAIL SERVER'
    app.config['MAIL_PORT'] = 'MAIL PORT'
    app.config['MAIL_USERNAME'] = 'MAIL SERVER USERNAME'
    app.config['MAIL_PASSWORD'] = 'MAIL SERVER APSSWORD'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True


    mail.init_app(app)
    sm = Sitemap(app=app)
    csrf = CSRFProtect(app)
    csrf.init_app(app)
    mdeditor = MDEditor(app)
    Markdown(app)
    return app

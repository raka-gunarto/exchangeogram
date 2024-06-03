from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.login_view = 'routes.login'
login_manager.init_app(app)

from exchangeogram import routes, models

# login session user ID deserialisation

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

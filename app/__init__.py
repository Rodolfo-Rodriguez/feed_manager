from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

import sys

reload(sys)
sys.setdefaultencoding('utf8')

from .config import Config

app = Flask(__name__)

CONFIG = Config()

app.config["SQLALCHEMY_DATABASE_URI"] = CONFIG.SQLITE_DATABASE
app.config['SECRET_KEY'] = "CocoCoco"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

from .bookmark import BookmarkManager 
bookmark_manager = BookmarkManager()

from .dbman import DBManager
db_manager = DBManager(db)

from .views_base import base
from .views_radio import radio
from .views_podcast import podcast

app.register_blueprint(base)
app.register_blueprint(radio)
app.register_blueprint(podcast)

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_cors import CORS

# INITIALIZING SECTION
db = SQLAlchemy()
migrate = Migrate()
moment = Moment()

 # Init app
app = Flask(__name__)
CORS(app)

# Link the config
app.config.from_object(Config)

# Register Packages
db.init_app(app)
migrate.init_app(app, db)
moment.init_app(app)


from app import models
from app import routes
from app import auth

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# INITIALIZING SECTION
db = SQLAlchemy()
migrate = Migrate()
moment = Moment()
jwt = JWTManager()

 # Init app
app = Flask(__name__)
CORS(app)

# Link the config
app.config.from_object(Config)

# Register Packages
db.init_app(app)
migrate.init_app(app, db)
moment.init_app(app)
jwt.init_app(app)


from app import models
from app import routes

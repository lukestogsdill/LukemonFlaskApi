from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from waitress import serve

# INITIALIZING SECTION
db = SQLAlchemy()
migrate = Migrate()
moment = Moment()
cors = CORS()
bcrypt = Bcrypt()

 # Init app

app = Flask(__name__)


# Link the config
app.config.from_object(Config)

# Register Packages
db.init_app(app)
migrate.init_app(app, db)
moment.init_app(app)
cors.init_app(app)
bcrypt.init_app(app)

from app import models
from app import routes
from app import auth

if __name__ == "__main__":
    serve(app, host='127.0.0.1', port=8080)


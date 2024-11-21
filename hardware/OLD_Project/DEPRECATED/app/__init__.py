from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_crontab import Crontab
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
crontab = Crontab(app)
CORS(app, resources={r"/socket.io/*": {"origins": "*"}})
app.config.from_object('app.config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app, cors_allowed_origins='*')

from app import models, routes, tasks, socket, controllers
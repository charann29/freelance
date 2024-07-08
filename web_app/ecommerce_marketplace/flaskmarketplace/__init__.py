from flask import  Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app=Flask(__name__)

DB_PASSWORD="root"
DB_USER="root"


app.config["SECRET_KEY"] = "key"
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@localhost/flaskmarketdb"
app.config['FLASK_ADMIN_SWATCH'] = "cerulean"

db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
app.app_context().push()

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

db.Model.metadata.reflect(db.engine)

from flaskmarketplace import routes 
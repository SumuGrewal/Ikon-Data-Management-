from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
db_name = "database.db"

def createApp():
    # create and configure the app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'qwerty'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable the warning

    db.init_app(app)
   
    migrate = Migrate(app, db)  # initialize flask-migrate here

    with app.app_context():
        from IkonConveyancing.app import routes  # import routes within app context

    from IkonConveyancing.app.models import User  # ensure all models are imported
   
    createDatabase(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
   
def createDatabase(app):
    # create the database if it doesn't exist
    if not path.exists(f'IkonConveyancing/{db_name}'):
        with app.app_context():
            db.create_all()
        print(
         "------------------------------------\n"
            "database initialized and created \n"
            "------------------------------------\n"
            "2024. made with 💖 by khush\n"
        )
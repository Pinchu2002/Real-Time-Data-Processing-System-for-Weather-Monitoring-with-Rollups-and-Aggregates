from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """
    Application factory function to create and configure the Flask app.
    """
    # Get the root path of the project
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Initialize Flask with explicit template and static folders
    app = Flask(
        __name__,
        template_folder=os.path.join(root_path, 'templates'),
        static_folder=os.path.join(root_path, 'static')
    )
    
    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models to ensure they are known to SQLAlchemy
    from . import models
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
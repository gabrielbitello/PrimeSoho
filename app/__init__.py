from flask import Flask
from .forms.routes import bp 

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    app.register_blueprint(bp)
    
    return app

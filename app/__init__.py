import os
from flask import Flask
from .routes import bp

def create_app():
    base_dir = os.path.dirname(__file__)
    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    app.register_blueprint(bp)
    app.secret_key = "hemmelig-nok"
    print("TEMPLATES:", app.jinja_loader.searchpath)
    print("STATIC:", app.static_folder)
    return app
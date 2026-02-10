from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "enkel-hemmelig-nok-for-skole"

    # Kobler på routes (Blueprint)
    from .routes import bp
    app.register_blueprint(bp)

    return app

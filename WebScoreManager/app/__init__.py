from flask import Flask
from flask_wtf import CSRFProtect

from .config import SECRET_KEY
from .security import register_csrf_error_handler

csrf = CSRFProtect()
app: Flask | None = None


def create_app() -> Flask:
    global app
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    csrf.init_app(app)
    register_csrf_error_handler(app)

    from .routes import register_routes

    register_routes()
    return app


app = create_app()

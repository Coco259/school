from flask import Flask
from pathlib import Path
from flask_wtf import CSRFProtect

from .config import SECRET_KEY
from .security import register_csrf_error_handler

csrf = CSRFProtect()
app: Flask | None = None


def create_app() -> Flask:
    global app
    # 明确指定模板与静态资源目录：当前包位于 WebScoreManager/app 下，
    # 实际 templates/static 放在上一级 WebScoreManager 目录。
    base_dir = Path(__file__).resolve().parent  # .../WebScoreManager/app
    project_root = base_dir.parent              # .../WebScoreManager
    templates = project_root / "templates"
    static = project_root / "static"

    app = Flask(
        __name__,
        template_folder=str(templates),
        static_folder=str(static),
        static_url_path="/static",
    )
    app.secret_key = SECRET_KEY

    csrf.init_app(app)
    register_csrf_error_handler(app)

    from .routes import register_routes

    register_routes()
    return app


app = create_app()

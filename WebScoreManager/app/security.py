from flask import jsonify, request, session
from flask_wtf.csrf import validate_csrf, CSRFError
from passlib.hash import pbkdf2_sha256


def hash_password(password: str | None) -> str | None:
    if password is None:
        return None
    return pbkdf2_sha256.hash(password)


def verify_password(password: str | None, hashed: str | None) -> bool:
    if hashed is None or hashed == '':
        return password is None or password == ''
    if not isinstance(hashed, str) or not hashed.startswith('$pbkdf2'):
        return password == hashed
    try:
        return pbkdf2_sha256.verify(password, hashed)
    except Exception:
        return False


def require_csrf():
    token = (
        request.headers.get('X-CSRFToken')
        or request.headers.get('X-CSRF-Token')
        or request.args.get('csrf_token')
    )
    try:
        validate_csrf(token)
        return None
    except Exception:
        return jsonify({'success': False, 'message': 'CSRF token missing or invalid'}), 400


def require_admin_session():
    if not session.get('is_login'):
        return jsonify({'success': False, 'message': '管理员未登录'}), 401
    return None


def register_csrf_error_handler(app):
    @app.errorhandler(CSRFError)
    def handle_csrf_error(err):
        return (
            jsonify(
                {
                    'success': False,
                    'message': err.description or 'CSRF token missing or invalid',
                }
            ),
            400,
        )

    return None

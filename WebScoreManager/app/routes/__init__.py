def register_routes():
    # Import route modules so decorators execute and attach to the Flask app.
    from . import auth, pages, students, courses, scores, statistics, passwords  # noqa: F401

    return None

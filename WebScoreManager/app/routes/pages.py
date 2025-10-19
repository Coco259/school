from flask import redirect, render_template, session

from .. import app


@app.route('/')
def login_page():
    return render_template('login.html')


@app.route('/index')
def index_page():
    if not session.get('is_login'):
        return redirect('/')
    return render_template('index.html')


@app.route('/student')
def student_page():
    if not session.get('is_login'):
        return redirect('/')
    return render_template('student.html')


@app.route('/student_login')
def student_login_page():
    return render_template('student_login.html')


@app.route('/student_portal')
def student_portal():
    if not session.get('is_student_login'):
        return redirect('/student_login')
    return render_template('student_portal.html')


@app.route('/course')
def course_page():
    if not session.get('is_login'):
        return redirect('/')
    return render_template('course.html')


@app.route('/statistics')
def statistics_page():
    if not session.get('is_login'):
        return redirect('/')
    return render_template('statistics.html')

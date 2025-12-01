from flask import jsonify, redirect, request, session
from flask_wtf.csrf import generate_csrf

from .. import app
from ..config import ADMIN_PASS_COL, ADMIN_TABLE, ADMIN_USER_COL, STUDENTS_TABLE, STUDENT_ID_COL
from ..db import get_db
from ..schemas import AdminLoginModel, StudentLoginModel, validate_json
from ..security import hash_password, verify_password


@app.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    token = generate_csrf()
    return jsonify({'csrf_token': token})


@app.route('/api/login', methods=['POST'])
@validate_json(AdminLoginModel)
def login():
    data = request.parsed
    username = data.username
    password = data.password

    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {ADMIN_TABLE} WHERE {ADMIN_USER_COL} = %s", (username,))
    admin = cursor.fetchone()
    if admin:
        stored = admin.get(ADMIN_PASS_COL)
        if verify_password(password, stored):
            if stored and (not isinstance(stored, str) or not stored.startswith('$pbkdf2')):
                try:
                    new_hash = hash_password(password)
                    cursor.execute(
                        f"UPDATE {ADMIN_TABLE} SET {ADMIN_PASS_COL}=%s WHERE {ADMIN_USER_COL}=%s",
                        (new_hash, username),
                    )
                    db.commit()
                except Exception:
                    pass
            db.close()
            session['is_login'] = True
            return jsonify({'success': True})
    db.close()
    return jsonify({'success': False, 'message': '账号或密码错误'})


@app.route('/logout')
def logout():
    session.pop('is_login', None)
    session.pop('is_student_login', None)
    session.pop('student_id', None)
    return redirect('/')


@app.route('/api/student_login', methods=['POST'])
@validate_json(StudentLoginModel)
def student_login():
    parsed = request.parsed
    student_id = parsed.student_id
    password = parsed.password
    try:
        student_id = int(student_id)
    except Exception:
        pass

    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {STUDENTS_TABLE} WHERE {STUDENT_ID_COL} = %s", (student_id,))
    student = cursor.fetchone()

    if not student:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': '学号不存在'})

    stored_pwd = student.get('password') if isinstance(student, dict) else None
    if verify_password(password, stored_pwd):
        if stored_pwd and (not isinstance(stored_pwd, str) or not stored_pwd.startswith('$pbkdf2')):
            try:
                new_hash = hash_password(password or '')
                cursor.execute(
                    f"UPDATE {STUDENTS_TABLE} SET password=%s WHERE {STUDENT_ID_COL}=%s",
                    (new_hash, student_id),
                )
                db.commit()
            except Exception:
                pass

        session['is_student_login'] = True
        session['student_id'] = (
            int(student.get(STUDENT_ID_COL)) if student.get(STUDENT_ID_COL) is not None else student_id
        )
        session['student_name'] = student.get('name')
        cursor.close()
        db.close()
        return jsonify({'success': True})

    cursor.close()
    db.close()
    return jsonify({'success': False, 'message': '密码错误'})

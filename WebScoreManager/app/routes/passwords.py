import secrets

from flask import jsonify, request, session

from .. import app
from ..config import ADMIN_PASS_COL, ADMIN_TABLE, STUDENTS_TABLE, STUDENT_ID_COL
from ..db import get_db
from ..schemas import AdminPasswordChangeModel, StudentPasswordChangeModel, validate_json
from ..security import hash_password, require_admin_session, verify_password


@app.route('/api/admin/password', methods=['PUT'])
@validate_json(AdminPasswordChangeModel)
def admin_change_password():
    data = request.parsed
    if not session.get('is_login'):
        return jsonify({'success': False, 'message': '管理员未登录'}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {ADMIN_TABLE} LIMIT 1")
    admin = cursor.fetchone()
    if not admin:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': 'admin not found'}), 500

    stored = admin.get(ADMIN_PASS_COL)
    if not verify_password(data.old_password, stored):
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': '旧密码错误'}), 400

    new_hash = hash_password(data.new_password)
    cursor.execute(f"UPDATE {ADMIN_TABLE} SET {ADMIN_PASS_COL}=%s", (new_hash,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True})


@app.route('/api/students/<int:student_id>/password', methods=['PUT'])
@validate_json(StudentPasswordChangeModel)
def student_change_password(student_id):
    data = request.parsed
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {STUDENTS_TABLE} WHERE {STUDENT_ID_COL} = %s", (student_id,))
    student = cursor.fetchone()
    if not student:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': 'student not found'}), 404

    if session.get('is_login'):
        new_hash = hash_password(data.new_password)
        cursor.execute(f"UPDATE {STUDENTS_TABLE} SET password=%s WHERE {STUDENT_ID_COL}=%s", (new_hash, student_id))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True})

    stored = student.get('password')
    if not verify_password(data.old_password, stored):
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': '旧密码错误'}), 400

    new_hash = hash_password(data.new_password)
    cursor.execute(f"UPDATE {STUDENTS_TABLE} SET password=%s WHERE {STUDENT_ID_COL}=%s", (new_hash, student_id))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True})


@app.route('/api/admin/students/<int:student_id>/reset_password', methods=['POST'])
def admin_reset_student_password(student_id):
    err = require_admin_session()
    if err:
        return err

    temp_pwd = secrets.token_urlsafe(8)
    pwd_hash = hash_password(temp_pwd)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {STUDENTS_TABLE} WHERE {STUDENT_ID_COL} = %s", (student_id,))
    if not cursor.fetchone():
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': 'student not found'}), 404

    cursor.execute(f"UPDATE {STUDENTS_TABLE} SET password=%s WHERE {STUDENT_ID_COL}=%s", (pwd_hash, student_id))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True, 'temp_password': temp_pwd})

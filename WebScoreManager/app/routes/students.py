from flask import jsonify, request

from .. import app
from ..config import (
    SCORES_TABLE,
    SCORE_STUDENT_ID_COL,
    STUDENTS_TABLE,
    STUDENT_AGE_COL,
    STUDENT_CLASS_COL,
    STUDENT_GENDER_COL,
    STUDENT_ID_COL,
    STUDENT_NAME_COL,
)
from ..db import get_db
from ..schemas import StudentCreateModel, StudentUpdateModel, validate_json
from ..security import hash_password, require_csrf


@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {STUDENTS_TABLE} WHERE {STUDENT_ID_COL} = %s", (student_id,))
    student = cursor.fetchone()
    db.close()
    return jsonify(student)


@app.route('/api/students/<int:student_id>', methods=['PUT'])
@validate_json(StudentUpdateModel)
def update_student(student_id):
    data = request.parsed
    db = get_db()
    cursor = db.cursor()

    updates = []
    values: list = []
    field_mapping = {
        STUDENT_NAME_COL: data.name,
        STUDENT_GENDER_COL: data.gender,
        STUDENT_AGE_COL: data.age,
        STUDENT_CLASS_COL: data.class_,
    }
    for column, value in field_mapping.items():
        if value is not None:
            updates.append(f"{column}=%s")
            values.append(value)

    if not updates:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': '没有可更新的字段'}), 400

    values.append(student_id)
    cursor.execute(
        f"UPDATE {STUDENTS_TABLE} SET {', '.join(updates)} WHERE {STUDENT_ID_COL}=%s",
        tuple(values),
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True})


@app.route('/api/students', methods=['POST'])
@validate_json(StudentCreateModel)
def add_student():
    data = request.parsed

    db = get_db()
    cursor = db.cursor()

    columns = [STUDENT_NAME_COL, STUDENT_GENDER_COL, STUDENT_AGE_COL, STUDENT_CLASS_COL]
    values = [data.name, data.gender, data.age, data.class_]
    placeholders = ['%s'] * len(columns)

    if data.password is not None:
        columns.append('password')
        values.append(hash_password(data.password))
        placeholders.append('%s')

    if data.student_id is not None:
        columns.insert(0, STUDENT_ID_COL)
        values.insert(0, data.student_id)
        placeholders.insert(0, '%s')

    cursor.execute(
        f"INSERT INTO {STUDENTS_TABLE} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})",
        tuple(values),
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True})


@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    err = require_csrf()
    if err:
        return err

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(f"DELETE FROM {SCORES_TABLE} WHERE {SCORE_STUDENT_ID_COL} = %s", (student_id,))
    except Exception:
        pass
    cursor.execute(f"DELETE FROM {STUDENTS_TABLE} WHERE {STUDENT_ID_COL} = %s", (student_id,))
    db.commit()
    db.close()
    return jsonify({'success': True})


@app.route('/api/students', methods=['GET'])
def list_students():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {STUDENTS_TABLE}")
    students = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(students)

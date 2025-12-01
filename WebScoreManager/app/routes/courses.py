from flask import jsonify, request

from .. import app
from ..config import (
    COURSES_TABLE,
    COURSE_ID_COL,
    COURSE_NAME_COL,
    COURSE_TEACHER_COL,
)
from ..db import get_db
from ..security import require_csrf


@app.route('/api/courses', methods=['GET'])
def get_courses():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {COURSES_TABLE}")
    courses = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(courses)


@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {COURSES_TABLE} WHERE {COURSE_ID_COL} = %s", (course_id,))
    course = cursor.fetchone()
    cursor.close()
    db.close()
    return jsonify(course)


@app.route('/api/courses', methods=['POST'])
def add_course():
    err = require_csrf()
    if err:
        return err

    data = request.json or {}
    db = get_db()
    cursor = db.cursor()
    if data.get('teacher') is not None:
        cursor.execute(
            f"INSERT INTO {COURSES_TABLE} ({COURSE_NAME_COL}, {COURSE_TEACHER_COL}) VALUES (%s, %s)",
            (data['course_name'], data['teacher']),
        )
    else:
        cursor.execute(
            f"INSERT INTO {COURSES_TABLE} ({COURSE_NAME_COL}) VALUES (%s)",
            (data['course_name'],),
        )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True})


@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    err = require_csrf()
    if err:
        return err

    data = request.json or {}
    db = get_db()
    cursor = db.cursor()
    if data.get('teacher') is not None:
        cursor.execute(
            f"UPDATE {COURSES_TABLE} SET {COURSE_NAME_COL}=%s, {COURSE_TEACHER_COL}=%s WHERE {COURSE_ID_COL}=%s",
            (data.get('course_name'), data.get('teacher'), course_id),
        )
    else:
        cursor.execute(
            f"UPDATE {COURSES_TABLE} SET {COURSE_NAME_COL}=%s WHERE {COURSE_ID_COL}=%s",
            (data.get('course_name'), course_id),
        )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True})


@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    err = require_csrf()
    if err:
        return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM {COURSES_TABLE} WHERE {COURSE_ID_COL} = %s", (course_id,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True})

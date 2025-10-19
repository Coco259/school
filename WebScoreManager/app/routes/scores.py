from flask import jsonify, request, session

from .. import app
from ..config import (
    COURSES_TABLE,
    COURSE_ID_COL,
    SCORES_TABLE,
    SCORE_COURSE_ID_COL,
    SCORE_ID_COL,
    SCORE_SCORE_COL,
    SCORE_STUDENT_ID_COL,
    STUDENTS_TABLE,
    STUDENT_ID_COL,
)
from ..db import get_db
from ..schemas import ScoreCreateModel, ScoreUpdateModel, validate_json
from ..security import require_csrf


@app.route('/api/scores/<int:score_id>', methods=['GET'])
def get_score(score_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {SCORES_TABLE} WHERE {SCORE_ID_COL} = %s", (score_id,))
    score = cursor.fetchone()
    cursor.close()
    db.close()
    return jsonify(score)


@app.route('/api/scores', methods=['GET'])
def list_scores():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {SCORES_TABLE}")
    scores = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(scores)


@app.route('/api/scores/<int:score_id>', methods=['DELETE'])
def delete_score(score_id):
    err = require_csrf()
    if err:
        return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM {SCORES_TABLE} WHERE {SCORE_ID_COL} = %s", (score_id,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True})


@app.route('/api/scores', methods=['POST'])
@validate_json(ScoreCreateModel)
def add_score():
    data = request.parsed
    db = get_db()
    cursor = db.cursor()

    if data.score < 0 or data.score > 100:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': 'score must be between 0 and 100', 'field': 'score'}), 400

    cursor.execute(f"SELECT 1 FROM {STUDENTS_TABLE} WHERE {STUDENT_ID_COL} = %s", (data.student_id,))
    if cursor.fetchone() is None:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': 'student_id not found', 'field': 'student_id'}), 400

    cursor.execute(f"SELECT 1 FROM {COURSES_TABLE} WHERE {COURSE_ID_COL} = %s", (data.course_id,))
    if cursor.fetchone() is None:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': 'course_id not found', 'field': 'course_id'}), 400

    cursor.execute(
        f"INSERT INTO {SCORES_TABLE} ({SCORE_STUDENT_ID_COL}, {SCORE_COURSE_ID_COL}, {SCORE_SCORE_COL}) VALUES (%s, %s, %s)",
        (data.student_id, data.course_id, data.score),
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True})


@app.route('/api/scores/<int:score_id>', methods=['PUT'])
@validate_json(ScoreUpdateModel)
def update_score(score_id):
    data = request.parsed
    db = get_db()
    cursor = db.cursor()

    cursor.execute(f"SELECT * FROM {SCORES_TABLE} WHERE {SCORE_ID_COL} = %s", (score_id,))
    existing = cursor.fetchone()
    if not existing:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': 'score not found'}), 404

    final_student_id = (
        data.student_id if data.student_id is not None else existing.get(SCORE_STUDENT_ID_COL)
    )
    final_course_id = data.course_id if data.course_id is not None else existing.get(SCORE_COURSE_ID_COL)
    final_score = data.score if data.score is not None else existing.get(SCORE_SCORE_COL)

    if final_score is None or final_score < 0 or final_score > 100:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': 'score must be between 0 and 100', 'field': 'score'}), 400

    cursor.execute(f"SELECT 1 FROM {STUDENTS_TABLE} WHERE {STUDENT_ID_COL} = %s", (final_student_id,))
    if cursor.fetchone() is None:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': 'student_id not found', 'field': 'student_id'}), 400

    cursor.execute(f"SELECT 1 FROM {COURSES_TABLE} WHERE {COURSE_ID_COL} = %s", (final_course_id,))
    if cursor.fetchone() is None:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': 'course_id not found', 'field': 'course_id'}), 400

    cursor.execute(
        f"UPDATE {SCORES_TABLE} SET {SCORE_STUDENT_ID_COL}=%s, {SCORE_COURSE_ID_COL}=%s, {SCORE_SCORE_COL}=%s WHERE {SCORE_ID_COL}=%s",
        (final_student_id, final_course_id, final_score, score_id),
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True})


@app.route('/api/student_scores/<int:student_id>', methods=['GET'])
def get_student_scores(student_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {SCORES_TABLE} WHERE {SCORE_STUDENT_ID_COL} = %s", (student_id,))
    scores = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(scores)


@app.route('/api/student_scores/me', methods=['GET'])
def get_my_scores():
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({'success': False, 'message': '未登录'}), 401
    return get_student_scores(int(student_id))

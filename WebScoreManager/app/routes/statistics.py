from flask import jsonify

from .. import app
from ..config import (
    COURSES_TABLE,
    COURSE_ID_COL,
    COURSE_NAME_COL,
    SCORES_TABLE,
    SCORE_COURSE_ID_COL,
    SCORE_ID_COL,
    SCORE_SCORE_COL,
    SCORE_STUDENT_ID_COL,
    STUDENTS_TABLE,
    STUDENT_CLASS_COL,
    STUDENT_ID_COL,
    STUDENT_NAME_COL,
)
from ..db import get_db
from ..security import require_admin_session


@app.route('/api/statistics/classes', methods=['GET'])
def list_classes():
    err = require_admin_session()
    if err:
        return err
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"SELECT DISTINCT {STUDENT_CLASS_COL} AS class_name FROM {STUDENTS_TABLE} "
        f"WHERE {STUDENT_CLASS_COL} IS NOT NULL AND {STUDENT_CLASS_COL} <> '' "
        f"ORDER BY {STUDENT_CLASS_COL}"
    )
    classes = [row['class_name'] for row in cursor.fetchall() if row.get('class_name')]
    cursor.close()
    db.close()
    return jsonify(classes)


@app.route('/api/statistics/courses', methods=['GET'])
def list_course_options():
    err = require_admin_session()
    if err:
        return err
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT {COURSE_ID_COL} AS course_id, {COURSE_NAME_COL} AS course_name FROM {COURSES_TABLE}")
    courses = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(courses)


@app.route('/api/statistics/class/<class_name>', methods=['GET'])
def class_statistics(class_name):
    err = require_admin_session()
    if err:
        return err
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        f"SELECT AVG(sc.{SCORE_SCORE_COL}) AS average_score, "
        f"MAX(sc.{SCORE_SCORE_COL}) AS max_score, "
        f"MIN(sc.{SCORE_SCORE_COL}) AS min_score, "
        f"COUNT(sc.{SCORE_ID_COL}) AS count_entries "
        f"FROM {SCORES_TABLE} sc "
        f"JOIN {STUDENTS_TABLE} s ON sc.{SCORE_STUDENT_ID_COL} = s.{STUDENT_ID_COL} "
        f"WHERE s.{STUDENT_CLASS_COL} = %s",
        (class_name,),
    )
    summary = cursor.fetchone() or {}

    cursor.execute(
        f"SELECT s.{STUDENT_ID_COL} AS student_id, s.{STUDENT_NAME_COL} AS name, "
        f"AVG(sc.{SCORE_SCORE_COL}) AS average_score, "
        f"SUM(sc.{SCORE_SCORE_COL}) AS total_score "
        f"FROM {SCORES_TABLE} sc "
        f"JOIN {STUDENTS_TABLE} s ON sc.{SCORE_STUDENT_ID_COL} = s.{STUDENT_ID_COL} "
        f"WHERE s.{STUDENT_CLASS_COL} = %s "
        f"GROUP BY s.{STUDENT_ID_COL} "
        f"ORDER BY total_score DESC",
        (class_name,),
    )
    student_rows = cursor.fetchall()

    cursor.execute(
        f"SELECT sc.{SCORE_SCORE_COL} AS score "
        f"FROM {SCORES_TABLE} sc "
        f"JOIN {STUDENTS_TABLE} s ON sc.{SCORE_STUDENT_ID_COL} = s.{STUDENT_ID_COL} "
        f"WHERE s.{STUDENT_CLASS_COL} = %s",
        (class_name,),
    )
    score_rows = cursor.fetchall()
    cursor.close()
    db.close()

    scores = [float(row['score']) for row in score_rows if row.get('score') is not None]
    buckets = [
        ('<60', 0, 59.99),
        ('60-69', 60, 69.99),
        ('70-79', 70, 79.99),
        ('80-89', 80, 89.99),
        ('90-100', 90, 100),
    ]
    distribution = []
    for label, low, high in buckets:
        count = sum(1 for value in scores if low <= value <= high)
        distribution.append({'label': label, 'count': count})

    response = {
        'class_name': class_name,
        'summary': {
            'average_score': float(summary['average_score']) if summary.get('average_score') is not None else None,
            'max_score': float(summary['max_score']) if summary.get('max_score') is not None else None,
            'min_score': float(summary['min_score']) if summary.get('min_score') is not None else None,
            'count_entries': int(summary['count_entries']) if summary.get('count_entries') is not None else 0,
        },
        'students': [
            {
                'student_id': row['student_id'],
                'name': row['name'],
                'average_score': float(row['average_score']) if row.get('average_score') is not None else None,
                'total_score': float(row['total_score']) if row.get('total_score') is not None else None,
            }
            for row in student_rows
        ],
        'distribution': distribution,
    }
    return jsonify(response)


@app.route('/api/statistics/course/<int:course_id>', methods=['GET'])
def course_statistics(course_id):
    err = require_admin_session()
    if err:
        return err
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        f"SELECT c.{COURSE_NAME_COL} AS course_name, "
        f"AVG(sc.{SCORE_SCORE_COL}) AS average_score, "
        f"MAX(sc.{SCORE_SCORE_COL}) AS max_score, "
        f"MIN(sc.{SCORE_SCORE_COL}) AS min_score, "
        f"COUNT(sc.{SCORE_ID_COL}) AS count_entries "
        f"FROM {COURSES_TABLE} c "
        f"LEFT JOIN {SCORES_TABLE} sc ON sc.{SCORE_COURSE_ID_COL} = c.{COURSE_ID_COL} "
        f"WHERE c.{COURSE_ID_COL} = %s",
        (course_id,),
    )
    summary = cursor.fetchone()
    if not summary or summary.get('course_name') is None:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': 'course not found'}), 404

    cursor.execute(
        f"SELECT sc.{SCORE_SCORE_COL} AS score "
        f"FROM {SCORES_TABLE} sc "
        f"WHERE sc.{SCORE_COURSE_ID_COL} = %s",
        (course_id,),
    )
    score_rows = cursor.fetchall()

    cursor.execute(
        f"SELECT s.{STUDENT_ID_COL} AS student_id, s.{STUDENT_NAME_COL} AS name, sc.{SCORE_SCORE_COL} AS score "
        f"FROM {SCORES_TABLE} sc "
        f"JOIN {STUDENTS_TABLE} s ON sc.{SCORE_STUDENT_ID_COL} = s.{STUDENT_ID_COL} "
        f"WHERE sc.{SCORE_COURSE_ID_COL} = %s "
        f"ORDER BY sc.{SCORE_SCORE_COL} DESC "
        f"LIMIT 10",
        (course_id,),
    )
    top_students = cursor.fetchall()
    cursor.close()
    db.close()

    scores = [float(row['score']) for row in score_rows if row.get('score') is not None]
    buckets = [
        ('<60', 0, 59.99),
        ('60-69', 60, 69.99),
        ('70-79', 70, 79.99),
        ('80-89', 80, 89.99),
        ('90-100', 90, 100),
    ]
    distribution = []
    for label, low, high in buckets:
        count = sum(1 for value in scores if low <= value <= high)
        distribution.append({'label': label, 'count': count})

    response = {
        'course_id': course_id,
        'course_name': summary.get('course_name'),
        'summary': {
            'average_score': float(summary['average_score']) if summary.get('average_score') is not None else None,
            'max_score': float(summary['max_score']) if summary.get('max_score') is not None else None,
            'min_score': float(summary['min_score']) if summary.get('min_score') is not None else None,
            'count_entries': int(summary['count_entries']) if summary.get('count_entries') is not None else 0,
        },
        'distribution': distribution,
        'top_students': [
            {
                'student_id': row['student_id'],
                'name': row['name'],
                'score': float(row['score']) if row.get('score') is not None else None,
            }
            for row in top_students
        ],
    }
    return jsonify(response)

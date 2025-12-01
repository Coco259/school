import uuid

import requests

BASE = 'http://127.0.0.1:5000'


def test_missing_csrf_rejected(app_server):
    session = requests.Session()
    payload = {'course_name': 'No CSRF'}
    resp = session.post(f'{BASE}/api/courses', json=payload)
    assert resp.status_code == 400
    data = resp.json()
    assert not data.get('success', False)
    assert 'CSRF' in data.get('message', '').upper()


def test_score_out_of_range(admin_session):
    unique_tag = uuid.uuid4().hex[:6]
    course_payload = {'course_name': f'Limit Course {unique_tag}', 'teacher': 'Edge'}
    resp_course = admin_session.post(f'{BASE}/api/courses', json=course_payload)
    assert resp_course.status_code == 200

    student_payload = {
        'name': f'Limit Student {unique_tag}',
        'gender': '男',
        'age': 18,
        'class': 'Limit'
    }
    resp_student = admin_session.post(f'{BASE}/api/students', json=student_payload)
    assert resp_student.status_code == 200

    students = admin_session.get(f'{BASE}/api/students').json()
    student_id = next(st['student_id'] for st in students if st['name'] == student_payload['name'])
    courses = admin_session.get(f'{BASE}/api/courses').json()
    course_id = next(c['course_id'] for c in courses if c['course_name'] == course_payload['course_name'])

    bad_score = {'student_id': student_id, 'course_id': course_id, 'score': 150}
    resp_bad = admin_session.post(f'{BASE}/api/scores', json=bad_score)
    assert resp_bad.status_code == 400
    data = resp_bad.json()
    assert data.get('message')

    admin_session.delete(f'{BASE}/api/students/{student_id}')
    admin_session.delete(f'{BASE}/api/courses/{course_id}')


def test_student_scores_requires_login(app_server):
    session = requests.Session()
    resp = session.get(f'{BASE}/api/student_scores/me')
    assert resp.status_code == 401


def test_statistics_requires_admin(app_server):
    session = requests.Session()
    resp = session.get(f'{BASE}/api/statistics/classes')
    assert resp.status_code == 401

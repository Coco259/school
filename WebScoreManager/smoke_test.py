import http.cookiejar
import urllib.request
import urllib.parse
import urllib.error
import json
import sys
import time

BASE = 'http://127.0.0.1:5000'


def req_opener():
    cj = http.cookiejar.CookieJar()
    handler = urllib.request.HTTPCookieProcessor(cj)
    return urllib.request.build_opener(handler)


def json_request(opener, path, method='GET', data=None):
    url = BASE + path
    headers = {'Content-Type': 'application/json'}
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with opener.open(req, timeout=10) as r:
            text = r.read().decode('utf-8')
            try:
                return r.status, json.loads(text)
            except Exception:
                return r.status, text
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read().decode('utf-8')
        except Exception:
            return e.code, str(e)
    except Exception as e:
        return None, str(e)


def run():
    print('Starting enhanced smoke tests against', BASE)
    opener = req_opener()

    # Admin login (setup_db.sql default admin: admin/admin)
    print('\n1) Admin login')
    status, body = json_request(opener, '/api/login', 'POST', {'username': 'admin', 'password': 'admin'})
    print('Status:', status, 'Body:', body)
    if status != 200:
        print('Admin login failed; aborting smoke test.')
        return

    # Create a course
    print('\n2) Create course')
    status, body = json_request(opener, '/api/courses', 'POST', {'course_name': 'Smoke Test Course', 'teacher': 'Auto'})
    print('Create course:', status, body)
    course_id = None
    # If API didn't return id, fetch courses list and find by name
    if status == 200 and isinstance(body, dict):
        course_id = body.get('course_id') or body.get('id') or None
    if course_id is None:
        s, b = json_request(opener, '/api/courses', 'GET')
        if s == 200 and isinstance(b, list):
            for c in b:
                if c.get('course_name') == 'Smoke Test Course':
                    course_id = c.get('course_id') or c.get('id')
                    break

    # Create a student
    print('\n3) Create student')
    stud = {'student_id': 's_smoke_1', 'name': 'Smoke Student', 'gender': 'M', 'age': 18, 'class': '1A', 'password': 's123'}
    status, body = json_request(opener, '/api/students', 'POST', stud)
    print('Create student:', status, body)
    # find the created student id (students table uses numeric student_id)
    student_id = None
    if status == 200:
        s, b = json_request(opener, '/api/students', 'GET')
        if s == 200 and isinstance(b, list):
            for st in b:
                if st.get('name') == stud['name']:
                    student_id = st.get('student_id') or st.get('id')
                    break
    if student_id is None:
        print('Could not determine created student id; aborting')
        return

    # Create a score for that student
    print('\n4) Create score')
    score_payload = {'student_id': student_id, 'course_id': course_id or 1, 'score': 95.5}
    status, body = json_request(opener, '/api/scores', 'POST', score_payload)
    print('Create score:', status, body)
    score_id = None
    if status == 200 and isinstance(body, dict):
        score_id = body.get('score_id') or body.get('id') or None

    # Student login
    print('\n5) Student login')
    student_opener = req_opener()
    status, body = json_request(student_opener, '/api/student_login', 'POST', {'student_id': student_id, 'password': 's123'})
    print('Student login status:', status, body)

    # Fetch student scores via /api/student_scores/me
    print('\n6) Fetch /api/student_scores/me')
    status, body = json_request(student_opener, '/api/student_scores/me', 'GET')
    print('Status:', status, 'Body:', body)

    # Cleanup: delete score, student, course
    print('\n7) Cleanup: delete score/student/course')
    if score_id:
        s, b = json_request(opener, f'/api/scores/{score_id}', 'DELETE')
        print('Delete score:', s, b)
    # delete by numeric student_id determined earlier
    s, b = json_request(opener, f"/api/students/{student_id}", 'DELETE')
    print('Delete student:', s, b)
    if course_id:
        s, b = json_request(opener, f'/api/courses/{course_id}', 'DELETE')
        print('Delete course:', s, b)

    print('\nEnhanced smoke tests finished.')


if __name__ == '__main__':
    run()


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


def json_request(opener, path, method='GET', data=None, extra_headers=None):
    url = BASE + path
    headers = {'Content-Type': 'application/json'}
    if extra_headers:
        headers.update(extra_headers)
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

    # fetch CSRF token for API write operations
    status, body = json_request(opener, '/api/csrf-token', 'GET')
    csrf_token = None
    if status == 200 and isinstance(body, dict):
        csrf_token = body.get('csrf_token')
    print('CSRF token fetched:', csrf_token)

    # prepare deletion headers once so it's always available in cleanup
    del_headers = {}
    if csrf_token:
        del_headers['X-CSRFToken'] = csrf_token

    # Admin login (setup_db.sql default admin was admin/admin, updated to admin/admin123)
    print('\n1) Admin login')
    login_headers = {}
    if csrf_token:
        login_headers['X-CSRFToken'] = csrf_token
    status, body = json_request(opener, '/api/login', 'POST', {'username': 'admin', 'password': 'admin123'}, extra_headers=login_headers)
    print('Status:', status, 'Body:', body)
    if status != 200:
        print('Admin login failed; aborting smoke test.')
        return

    # Create a course
    print('\n2) Create course')
    # create course (include CSRF token)
    course_headers = {}
    if csrf_token:
        course_headers['X-CSRFToken'] = csrf_token
    status, body = json_request(opener, '/api/courses', 'POST', {'course_name': 'Smoke Test Course', 'teacher': 'Auto'}, extra_headers=course_headers)
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
    # create student (include CSRF)
    stud_headers = {}
    if csrf_token:
        stud_headers['X-CSRFToken'] = csrf_token
    status, body = json_request(opener, '/api/students', 'POST', stud, extra_headers=stud_headers)
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
    # create score (include CSRF)
    score_headers = {}
    if csrf_token:
        score_headers['X-CSRFToken'] = csrf_token
    status, body = json_request(opener, '/api/scores', 'POST', score_payload, extra_headers=score_headers)
    print('Create score:', status, body)
    score_id = None
    if status == 200 and isinstance(body, dict):
        score_id = body.get('score_id') or body.get('id') or None

    # Student login
    print('\n5) Student login')
    student_opener = req_opener()
    # student login (student_opener should fetch its own csrf token if needed)
    # try to fetch token for student_opener
    s_status, s_body = json_request(student_opener, '/api/csrf-token', 'GET')
    s_csrf = None
    if s_status == 200 and isinstance(s_body, dict):
        s_csrf = s_body.get('csrf_token')
    s_headers = {}
    if s_csrf:
        s_headers['X-CSRFToken'] = s_csrf
    status, body = json_request(student_opener, '/api/student_login', 'POST', {'student_id': student_id, 'password': 's123'}, extra_headers=s_headers)
    print('Student login status:', status, body)

    # Fetch student scores via /api/student_scores/me
    print('\n6) Fetch /api/student_scores/me')
    status, body = json_request(student_opener, '/api/student_scores/me', 'GET')
    print('Status:', status, 'Body:', body)

    # Cleanup: delete score, student, course
    print('\n7) Cleanup: delete score/student/course')
    if score_id:
        # include CSRF when deleting
        s, b = json_request(opener, f'/api/scores/{score_id}', 'DELETE', extra_headers=del_headers)
        print('Delete score:', s, b)
    # delete by numeric student_id determined earlier
    s, b = json_request(opener, f"/api/students/{student_id}", 'DELETE', extra_headers=del_headers)
    print('Delete student:', s, b)
    if course_id:
        s, b = json_request(opener, f'/api/courses/{course_id}', 'DELETE', extra_headers=del_headers)
        print('Delete course:', s, b)

    print('\nEnhanced smoke tests finished.')


if __name__ == '__main__':
    run()


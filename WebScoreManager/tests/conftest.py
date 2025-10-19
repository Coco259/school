import os
import subprocess
import time

import pytest
import requests

BASE = 'http://127.0.0.1:5000'


def _server_alive(timeout=0.2):
    try:
        response = requests.get(f'{BASE}/api/csrf-token', timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope='session')
def app_server():
    if _server_alive():
        yield None
        return

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app_path = os.path.join(project_root, 'app.py')
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    proc = subprocess.Popen(
        ['python', app_path],
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    start_time = time.time()
    while time.time() - start_time < 20:
        if _server_alive():
            break
        time.sleep(0.5)
    else:
        try:
            output = proc.stdout.read().decode('utf-8', errors='ignore')
        except Exception:
            output = ''
        proc.terminate()
        raise RuntimeError('Flask server failed to start. Logs:\n' + output)

    try:
        yield proc
    finally:
        try:
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except Exception:
                    proc.kill()
        except Exception:
            pass


@pytest.fixture(scope='session')
def admin_session(app_server):
    session = requests.Session()
    token_response = session.get(f'{BASE}/api/csrf-token')
    token_response.raise_for_status()
    csrf_token = token_response.json()['csrf_token']
    session.headers.update({'X-CSRFToken': csrf_token})
    resp = session.post(f'{BASE}/api/login', json={'username': 'admin', 'password': 'admin123'})
    resp.raise_for_status()
    assert resp.json().get('success')
    return session


@pytest.fixture(scope='session')
def student_session(admin_session):
    session = requests.Session()
    token_response = session.get(f'{BASE}/api/csrf-token')
    token_response.raise_for_status()
    csrf_token = token_response.json()['csrf_token']
    session.headers.update({'X-CSRFToken': csrf_token})

    payload = {
        'name': 'Pytest Student',
        'gender': '男',
        'age': 18,
        'class': '1A',
        'password': 's123'
    }
    resp = admin_session.post(f'{BASE}/api/students', json=payload)
    resp.raise_for_status()

    students = admin_session.get(f'{BASE}/api/students').json()
    sid = next((st['student_id'] for st in students if st['name'] == payload['name']), None)
    assert sid is not None

    login_resp = session.post(f'{BASE}/api/student_login', json={'student_id': sid, 'password': 's123'})
    login_resp.raise_for_status()
    assert login_resp.json().get('success')
    session._student_id = sid
    return session

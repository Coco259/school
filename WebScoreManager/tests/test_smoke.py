BASE = 'http://127.0.0.1:5000'

def test_admin_login(admin_session):
    # 已在 fixture 登录
    pass

def test_create_course(admin_session):
    payload = {'course_name': 'Pytest Course', 'teacher': 'Auto'}
    resp = admin_session.post(f'{BASE}/api/courses', json=payload)
    assert resp.status_code == 200
    # 查找 course_id
    r2 = admin_session.get(f'{BASE}/api/courses')
    cid = None
    for c in r2.json():
        if c.get('course_name') == payload['course_name']:
            cid = c.get('course_id')
            break
    assert cid is not None
    test_create_course.course_id = cid

def test_create_score(admin_session, student_session):
    # 依赖 test_create_course
    if not hasattr(test_create_course, 'course_id'):
        test_create_course(admin_session)
    cid = test_create_course.course_id
    # 使用 student_session 中的学生 ID
    sid = getattr(student_session, '_student_id', None)
    assert sid is not None
    payload = {'student_id': sid, 'course_id': cid, 'score': 95.5}
    resp = admin_session.post(f'{BASE}/api/scores', json=payload)
    assert resp.status_code == 200
    test_create_score.score_id = None
    # 查找 score_id
    r3 = admin_session.get(f'{BASE}/api/scores')
    for sc in r3.json():
        if sc.get('student_id') == sid and sc.get('course_id') == cid:
            test_create_score.score_id = sc.get('score_id')
            break
    assert test_create_score.score_id is not None

def test_student_login(student_session):
    # 已在 fixture 登录
    pass

def test_get_scores(student_session):
    r = student_session.get(f'{BASE}/api/student_scores/me')
    assert r.status_code == 200
    scores = r.json()
    assert isinstance(scores, list)
    assert any(float(s['score']) == 95.5 for s in scores)

def test_cleanup(admin_session):
    # 删除成绩、学生、课程
    if hasattr(test_create_score, 'score_id'):
        resp = admin_session.delete(f'{BASE}/api/scores/{test_create_score.score_id}')
        assert resp.status_code == 200
    # 删除学生
    r2 = admin_session.get(f'{BASE}/api/students')
    sid = None
    for st in r2.json():
        if st.get('name') == 'Pytest Student':
            sid = st.get('student_id')
            break
    if sid:
        resp = admin_session.delete(f'{BASE}/api/students/{sid}')
        assert resp.status_code == 200
    # 删除课程
    r3 = admin_session.get(f'{BASE}/api/courses')
    cid = None
    for c in r3.json():
        if c.get('course_name') == 'Pytest Course':
            cid = c.get('course_id')
            break
    if cid:
        resp = admin_session.delete(f'{BASE}/api/courses/{cid}')
        assert resp.status_code == 200

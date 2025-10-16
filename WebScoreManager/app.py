from flask import Flask, render_template, request, redirect, session, jsonify
import pymysql

app = Flask(__name__)
app.secret_key = 'webscoremanager_secret_key'  # 用于session加密，可自定义

# 可配置的表/列名映射（根据你的实际数据库调整）
# 如果你的表或列名不同，只需在这里修改即可：
STUDENTS_TABLE = 'students'
STUDENT_ID_COL = 'student_id'
STUDENT_NAME_COL = 'name'
STUDENT_GENDER_COL = 'gender'
STUDENT_AGE_COL = 'age'
STUDENT_CLASS_COL = 'class'  # 建议改为 'class_name' 后在此处同步

COURSES_TABLE = 'courses'
COURSE_ID_COL = 'course_id'
COURSE_NAME_COL = 'course_name'
COURSE_TEACHER_COL = 'teacher'

SCORES_TABLE = 'scores'
SCORE_ID_COL = 'score_id'
SCORE_STUDENT_ID_COL = 'student_id'
SCORE_COURSE_ID_COL = 'course_id'
SCORE_SCORE_COL = 'score'

ADMIN_TABLE = 'admin'
ADMIN_USER_COL = 'username'
ADMIN_PASS_COL = 'password'

# 数据库连接函数，需修改为自己的MySQL配置
def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='y210093',  # 替换为你的MySQL密码
        database='school_db',  # 确保已创建school_db数据库
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor  # 查询结果返回字典
    )

# 登录页面路由
@app.route('/')
def login_page():
    return render_template('login.html')

# 登录验证接口
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {ADMIN_TABLE} WHERE {ADMIN_USER_COL} = %s AND {ADMIN_PASS_COL} = %s", (username, password))
    admin = cursor.fetchone()
    db.close()
    
    if admin:
        session['is_login'] = True
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "账号或密码错误"})

# 首页路由（需登录）
@app.route('/index')
def index_page():
    if not session.get('is_login'):
        return redirect('/')
    return render_template('index.html')

# 学生管理页面路由
@app.route('/student')
def student_page():
    if not session.get('is_login'):
        return redirect('/')
    return render_template('student.html')

# API：获取单个学生信息
@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {STUDENTS_TABLE} WHERE {STUDENT_ID_COL} = %s", (student_id,))
    student = cursor.fetchone()
    db.close()
    return jsonify(student)

# API：更新学生信息
@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"UPDATE {STUDENTS_TABLE} SET {STUDENT_NAME_COL}=%s, {STUDENT_GENDER_COL}=%s, {STUDENT_AGE_COL}=%s, {STUDENT_CLASS_COL}=%s WHERE {STUDENT_ID_COL}=%s",
        (data['name'], data['gender'], data['age'], data['class'], student_id)
    )
    db.commit()
    db.close()
    return jsonify({"success": True})

# API：添加学生
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json
    name = data.get('name')
    gender = data.get('gender')
    age = data.get('age')
    class_name = data.get('class')
    password = data.get('password')
    
    db = get_db()
    cursor = db.cursor()
    # 如果提供了 password，则插入 password 字段（兼容 setup_db.sql）
    if password is not None:
        cursor.execute(
            f"INSERT INTO {STUDENTS_TABLE} ({STUDENT_NAME_COL}, {STUDENT_GENDER_COL}, {STUDENT_AGE_COL}, {STUDENT_CLASS_COL}, password) VALUES (%s, %s, %s, %s, %s)",
            (name, gender, age, class_name, password)
        )
    else:
        cursor.execute(
            f"INSERT INTO {STUDENTS_TABLE} ({STUDENT_NAME_COL}, {STUDENT_GENDER_COL}, {STUDENT_AGE_COL}, {STUDENT_CLASS_COL}) VALUES (%s, %s, %s, %s)",
            (name, gender, age, class_name)
        )
    db.commit()
    db.close()
    return jsonify({"success": True})

# API：删除学生
@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    db = get_db()
    cursor = db.cursor()
    # 删除该学生的关联成绩以避免外键约束错误（如果 scores 表存在外键）
    try:
        cursor.execute(f"DELETE FROM {SCORES_TABLE} WHERE {SCORE_STUDENT_ID_COL} = %s", (student_id,))
    except Exception:
        # 如果 scores 表或列不存在，继续尝试删除学生（容错）
        pass
    cursor.execute(f"DELETE FROM {STUDENTS_TABLE} WHERE {STUDENT_ID_COL} = %s", (student_id,))
    db.commit()
    db.close()
    return jsonify({"success": True})

# 退出登录
@app.route('/logout')
def logout():
    session.pop('is_login', None)
    # also clear student session if present
    session.pop('is_student_login', None)
    session.pop('student_id', None)
    return redirect('/')


# 学生登录页面
@app.route('/student_login')
def student_login_page():
    return render_template('student_login.html')


# 学生登录验证（支持无密码或有 password 字段）
@app.route('/api/student_login', methods=['POST'])
def student_login():
    data = request.json
    student_id = data.get('student_id')
    password = data.get('password')
    try:
        # ensure integer id when possible
        student_id = int(student_id)
    except Exception:
        pass

    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {STUDENTS_TABLE} WHERE {STUDENT_ID_COL} = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    db.close()

    if not student:
        return jsonify({"success": False, "message": "学号不存在"})

    # 如果数据库中存在 password 字段，按以下规则验证：
    # - 如果存储的 password 为 NULL/空字符串，则允许不输密码直接登录
    # - 否则需要提供匹配的 password
    stored_pwd = student.get('password') if isinstance(student, dict) else None
    if stored_pwd is None or stored_pwd == '':
        session['is_student_login'] = True
        session['student_id'] = int(student.get(STUDENT_ID_COL)) if student.get(STUDENT_ID_COL) is not None else student_id
        session['student_name'] = student.get('name')
        return jsonify({"success": True})
    else:
        if password and password == stored_pwd:
            session['is_student_login'] = True
            session['student_id'] = int(student.get(STUDENT_ID_COL)) if student.get(STUDENT_ID_COL) is not None else student_id
            session['student_name'] = student.get('name')
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "密码错误"})


# 学生首页（查看自己成绩）
@app.route('/student_portal')
def student_portal():
    if not session.get('is_student_login'):
        return redirect('/student_login')
    return render_template('student_portal.html')


# API：获取指定学生的成绩
@app.route('/api/student_scores/<int:student_id>', methods=['GET'])
def get_student_scores(student_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {SCORES_TABLE} WHERE {SCORE_STUDENT_ID_COL} = %s", (student_id,))
    scores = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(scores)


# API：获取当前登录学生的成绩（基于 session）
@app.route('/api/student_scores/me', methods=['GET'])
def get_my_scores():
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({"success": False, "message": "未登录"}), 401
    return get_student_scores(int(student_id))

# 课程管理页面路由
@app.route('/course')
def course_page():
    if not session.get('is_login'):
        return redirect('/')
    return render_template('course.html')


# API：获取所有课程
@app.route('/api/courses', methods=['GET'])
def get_courses():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {COURSES_TABLE}")
    courses = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(courses)


# API：获取单个课程
@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {COURSES_TABLE} WHERE {COURSE_ID_COL} = %s", (course_id,))
    course = cursor.fetchone()
    cursor.close()
    db.close()
    return jsonify(course)


# API：更新课程
@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    # 构建可选的更新字段（如果数据库没有 teacher 列，则仅更新 course_name）
    if data.get('teacher') is not None:
        cursor.execute(
            f"UPDATE {COURSES_TABLE} SET {COURSE_NAME_COL}=%s, {COURSE_TEACHER_COL}=%s WHERE {COURSE_ID_COL}=%s",
            (data.get('course_name'), data.get('teacher'), course_id)
        )
    else:
        cursor.execute(
            f"UPDATE {COURSES_TABLE} SET {COURSE_NAME_COL}=%s WHERE {COURSE_ID_COL}=%s",
            (data.get('course_name'), course_id)
        )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"success": True})


# API：删除课程
@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM {COURSES_TABLE} WHERE {COURSE_ID_COL} = %s", (course_id,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"success": True})


# API：添加课程
@app.route('/api/courses', methods=['POST'])
def add_course():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    # 如果前端未提供 teacher 字段，尝试只插入 course_name（兼容旧表结构）
    if data.get('teacher') is not None:
        cursor.execute(
            f"INSERT INTO {COURSES_TABLE} ({COURSE_NAME_COL}, {COURSE_TEACHER_COL}) VALUES (%s, %s)",
            (data['course_name'], data['teacher'])
        )
    else:
        cursor.execute(
            f"INSERT INTO {COURSES_TABLE} ({COURSE_NAME_COL}) VALUES (%s)",
            (data['course_name'],)
        )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"success": True})



# API：获取所有学生（前端列表使用）
@app.route('/api/students', methods=['GET'])
def list_students():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {STUDENTS_TABLE}")
    students = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(students)


# 成绩管理页面路由
@app.route('/score')
def score_page():
    if not session.get('is_login'):
        return redirect('/')
    return render_template('score.html')


# API：获取所有成绩
@app.route('/api/scores', methods=['GET'])
def get_scores():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {SCORES_TABLE}")
    scores = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(scores)


# API：获取单个成绩
@app.route('/api/scores/<int:score_id>', methods=['GET'])
def get_score(score_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {SCORES_TABLE} WHERE {SCORE_ID_COL} = %s", (score_id,))
    score = cursor.fetchone()
    cursor.close()
    db.close()
    return jsonify(score)



# API：删除成绩
@app.route('/api/scores/<int:score_id>', methods=['DELETE'])
def delete_score(score_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM {SCORES_TABLE} WHERE {SCORE_ID_COL} = %s", (score_id,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"success": True})


# API：添加成绩
@app.route('/api/scores', methods=['POST'])
def add_score():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"INSERT INTO {SCORES_TABLE} ({SCORE_STUDENT_ID_COL}, {SCORE_COURSE_ID_COL}, {SCORE_SCORE_COL}) VALUES (%s, %s, %s)",
        (data['student_id'], data['course_id'], data['score'])
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"success": True})


# API：更新成绩
@app.route('/api/scores/<int:score_id>', methods=['PUT'])
def update_score(score_id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"UPDATE {SCORES_TABLE} SET {SCORE_STUDENT_ID_COL}=%s, {SCORE_COURSE_ID_COL}=%s, {SCORE_SCORE_COL}=%s WHERE {SCORE_ID_COL}=%s",
        (data.get('student_id'), data.get('course_id'), data.get('score'), score_id)
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)
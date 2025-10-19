# operations.py
from db_utils import execute, query

# ---------------------- 学生管理 ----------------------
def add_student(name, gender, age, class_name):
    """添加学生"""
    sql = """
    INSERT INTO students (name, gender, age, class) 
    VALUES (%s, %s, %s, %s)
    """
    return execute(sql, (name, gender, age, class_name))

def get_student_by_id(student_id):
    """通过学号查询学生"""
    sql = "SELECT * FROM students WHERE student_id = %s"
    return query(sql, (student_id,))

# ---------------------- 课程管理 ----------------------
def add_course(course_name, credit):
    """添加课程"""
    sql = "INSERT INTO courses (course_name, credit) VALUES (%s, %s)"
    return execute(sql, (course_name, credit))

def get_all_courses():
    """查询所有课程"""
    sql = "SELECT * FROM courses ORDER BY course_id"
    return query(sql)

# ---------------------- 成绩管理 ----------------------
def add_score(student_id, course_id, score):
    """添加成绩"""
    sql = "INSERT INTO scores (student_id, course_id, score) VALUES (%s, %s, %s)"
    return execute(sql, (student_id, course_id, score))

def get_student_scores(student_id):
    """查询学生的所有成绩（关联课程名）"""
    sql = """
    SELECT c.course_name, sc.score 
    FROM scores sc
    JOIN courses c ON sc.course_id = c.course_id
    WHERE sc.student_id = %s
    """
    return query(sql, (student_id,))

def update_score(score_id, new_score):
    """修改成绩"""
    sql = "UPDATE scores SET score = %s WHERE score_id = %s"
    return execute(sql, (new_score, score_id))
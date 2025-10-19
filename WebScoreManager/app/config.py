import os

SECRET_KEY = os.getenv('SECRET_KEY', 'webscoremanager_secret_key')

STUDENTS_TABLE = 'students'
STUDENT_ID_COL = 'student_id'
STUDENT_NAME_COL = 'name'
STUDENT_GENDER_COL = 'gender'
STUDENT_AGE_COL = 'age'
STUDENT_CLASS_COL = 'class'

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

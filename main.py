# main.py
from operations import (
    add_student, get_student_by_id,
    add_course, get_all_courses,
    add_score, get_student_scores, update_score
)

def test_student_ops():
    """测试学生相关操作"""
    print("=== 测试添加学生 ===")
    # 添加一名学生：姓名“赵六”，男，20岁，计算机3班
    rows = add_student("赵六", "男", 20, "计算机3班")
    print(f"添加成功，影响行数：{rows}")  # 成功应为1

    print("\n=== 测试查询学生 ===")
    # 查询学号为11的学生（假设刚添加的是第11条）
    student = get_student_by_id(11)
    if student:
        print(f"学号：{student[0][0]}，姓名：{student[0][1]}，班级：{student[0][4]}")

def test_score_ops():
    """测试成绩相关操作"""
    print("\n=== 测试添加成绩 ===")
    # 给学号11的学生添加“数据库原理”（course_id=1）的成绩88
    rows = add_score(11, 1, 88.0)
    print(f"添加成绩成功，影响行数：{rows}")

    print("\n=== 测试查询成绩 ===")
    scores = get_student_scores(11)
    if scores:
        for course_name, score in scores:
            print(f"课程：{course_name}，分数：{score}")

    print("\n=== 测试修改成绩 ===")
    # 假设刚添加的成绩score_id是31（根据实际数据调整）
    rows = update_score(31, 92.5)
    print(f"修改成绩成功，影响行数：{rows}")

if __name__ == "__main__":
    test_student_ops()
    test_score_ops()
-- setup_db.sql
-- 示例建表脚本，供开发/测试使用。请先在 MySQL 中创建数据库 `school_db`，然后运行：
-- mysql -u root -p < setup_db.sql

DROP DATABASE IF EXISTS school_db;
CREATE DATABASE school_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE school_db;

-- 管理员表（用于后台登录）
CREATE TABLE admin (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(64) NOT NULL UNIQUE,
  password VARCHAR(128) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 学生表
CREATE TABLE students (
  student_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  gender VARCHAR(8),
  age INT,
  `class` VARCHAR(100),
  password VARCHAR(128) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 课程表（包含 credit 字段以兼容现有数据库）
CREATE TABLE courses (
  course_id INT AUTO_INCREMENT PRIMARY KEY,
  course_name VARCHAR(200) NOT NULL,
  teacher VARCHAR(100) DEFAULT NULL,
  credit DECIMAL(4,1) NOT NULL DEFAULT 0.0,
  description TEXT DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 成绩表（使用 score_id 作为主键）
CREATE TABLE scores (
  score_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  course_id INT NOT NULL,
  score DECIMAL(5,2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 示例数据
INSERT INTO admin (username, password) VALUES ('admin', 'admin');

INSERT INTO courses (course_name, teacher, credit) VALUES
('语文', '张老师', 3.0),
('数学', '李老师', 4.0),
('英语', '王老师', 2.5);

INSERT INTO students (name, gender, age, `class`, password) VALUES
('张三', '男', 18, '高一(1)班', NULL),
('李四', '女', 17, '高一(2)班', NULL);

INSERT INTO scores (student_id, course_id, score) VALUES
(1, 1, 85.50),
(1, 2, 92.00),
(2, 1, 78.00);

-- 结束

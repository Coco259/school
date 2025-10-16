# WebScoreManager — 烟雾测试与设置

此文件夹包含一个基于 Flask 的小型学生/课程/成绩管理器。`smoke_test.py` 脚本执行端到端的冒烟测试（管理员登录、创建课程、创建学生、创建成绩、学生登录、获取成绩、清理）。

先决条件
- Python 3.10 及以上版本（推荐使用虚拟环境）
- MySQL 服务器（或 MariaDB）
- 列在 `requirements.txt` 中的依赖项（Flask、PyMySQL）

快速设置

1. 导入提供的 SQL 模式以创建一个干净的 `school_db` 并填充示例数据：

以 root 身份并输入密码运行 MySQL 命令，执行位于 D:\桌面\School_db\WebScoreManager 目录下的 setup_db.sql 脚本。```


2. （可选）创建并激活虚拟环境，安装依赖项：

python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt


创建虚拟环境：`python -m venv .venv`；激活虚拟环境：`.\.venv\Scripts\Activate.ps1`；安装依赖包：`pip install -r requirements```


3. 启动 Flask 应用程序（在 `WebScoreManager` 目录中）：

运行 `python app.py` 命令。```


4. 在另一个终端中运行冒烟测试：

运行 `python smoke_test.py` 命令。```


注意事项：
- 烟雾测试期望使用 `setup_db.sql` 中的默认管理员（用户名 `admin`，密码 `admin123`）。如果您更改了凭据，请相应地修改 `smoke_test.py`。
- 如果您现有的数据库模式不同，请导入 `setup_db.sql` 或编辑 `app.py` 中的顶部常量以匹配您的模式。
- 浏览器方式（最简单）
打开： http://127.0.0.1:5000/student_login
在表单中输入学号（student_id），如果该学生在 DB 中没有设置密码可留空；否则填写对应密码。
提交后成功会跳转到学生门户页面（/student_portal），可以查看成绩。
在当前后端实现中：
新增学生时可通过 POST /api/students 提交 password 字段（add_student 支持插入 password）。
PUT /api/students/<id>（update_student）当前实现不包含修改 password 的字段，所以无法通过该接口更新密码。
直接用 SQL 修改（推荐的简短方法）：

UPDATE students SET password='你的新密码' WHERE student_id=1;
在本地使用 Python 执行示例：
import pymysql
conn = pymysql.connect(host='localhost', user='root', password='y210093', database='school_db')
cur = conn.cursor()
cur.execute("UPDATE students SET password=%s WHERE student_id=%s", ('pass123', 1))
conn.commit()
cur.close()
conn.close()

管理员（admin）

用户名：admin
密码：admin123
Flask 运行： http://127.0.0.1:5000

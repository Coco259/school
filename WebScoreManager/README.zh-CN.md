````markdown
# WebScoreManager — 烟雾测试与快速部署

此目录包含一个基于 Flask 的简易学生/课程/成绩管理应用。`smoke_test.py` 脚本会执行端到端的烟雾测试（管理员登录、创建课程、创建学生、添加成绩、学生登录、获取成绩、清理测试数据）。

前提条件
- Python 3.10 及以上（建议使用虚拟环境 venv）
- MySQL 或 MariaDB 数据库服务
- 依赖见 `requirements.txt`（例如 Flask、PyMySQL）

快速上手

1. 导入提供的 SQL 模式以创建带示例数据的干净 `school_db`：

```powershell
mysql -u root -p < "d:\桌面\School_db\WebScoreManager\setup_db.sql"
```

2. （可选）创建并激活虚拟环境，然后安装依赖：

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

3. 启动 Flask 应用（在 `WebScoreManager` 目录下运行）：

```powershell
python app.py
```

4. 在另一个终端运行烟雾测试：

```powershell
python smoke_test.py
```

注意事项
- 烟雾测试默认使用 `setup_db.sql` 中的管理员账号（用户名 `admin`，密码 `admin123`）。若你更改了凭据，请相应修改 `smoke_test.py`。
- 如果你的现有数据库模式不同，请导入 `setup_db.sql` 或在 `app.py` 顶部调整常量以匹配你的模式。

````
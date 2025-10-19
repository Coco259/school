<!-- 为 AI 助手与自动代码生成器提供本仓库的关键上下文。请保持简洁、可操作、以中文为主。 -->

# Copilot 指南（WebScoreManager 版）

仓库概览
- 本仓库现包含一个 Flask 应用 WebScoreManager（目录 `WebScoreManager/`），以及根目录遗留的两个小模块：`import pymysql.py` 与 `sc`（均为简易 MySQL 执行器）。
- 当前主要开发目标集中在 WebScoreManager：学生/课程/成绩管理，登录认证，安全与验证，测试与 CI。

核心目录与文件
- `WebScoreManager/app.py`：Flask 主应用。
  - 常量：表名/列名映射（例如 `STUDENTS_TABLE`, `SCORES_TABLE` 等）。
  - DB 连接：`get_db()` 使用 PyMySQL 连接 MySQL（注意：当前凭据硬编码，仅用于本地开发）。
  - 密码：`hash_password`/`verify_password`（passlib.pbkdf2_sha256）。
  - 验证：pydantic 模型与 `@validate_json(Model)` 装饰器（在解析 JSON 前先执行 CSRF 校验，并在 `request.parsed` 提供已验证数据）。
  - CSRF：启用 flask-wtf；提供 `/api/csrf-token`，API 写操作从 `X-CSRFToken` 读取令牌。
  - 接口：学生/课程/成绩 CRUD、学生登录/门户、管理员登录、密码修改/重置；成绩写入包含外键存在性校验。
- `WebScoreManager/templates/`、`WebScoreManager/static/`：前端模板与静态资源。
- `WebScoreManager/setup_db.sql`：可复现实例库 schema（admin/students/courses/scores）。
- `WebScoreManager/requirements.txt`：依赖清单（Flask、pymysql、passlib、flask-wtf、pydantic、等）。
- `WebScoreManager/smoke_test.py`：历史烟雾测试脚本（urllib）。
- `WebScoreManager/tests/test_smoke.py`：pytest 端到端测试（requests + Session）。

关键约定（安全/校验/接口）
- 密码哈希：统一使用 `pbkdf2_sha256`（passlib）。所有保存/验证均走 `hash_password`/`verify_password`。不要新增明文存储或日志打印密码/哈希。
- CSRF：所有 POST/PUT/DELETE 必须校验 CSRF。前端/测试需先 GET `/api/csrf-token`，随后在请求头携带 `X-CSRFToken`。
- 参数校验：所有写接口应使用 `@validate_json(Model)` 并从 `request.parsed` 读取字段；校验失败返回 400，包含 `errors` 详情。
- 外键校验：`/api/scores` 的 POST/PUT 必须先检查 `student_id` 与 `course_id` 是否存在，否则返回 400。
- 会话约定：
  - 管理员登录成功后 `session['is_login']=True`；
  - 学生登录成功后 `session['is_student_login']=True`，并设置 `session['student_id']`。
- 密码接口：
  - `PUT /api/admin/password`：{old_password, new_password}，需管理员登录且验证旧密码。
  - `PUT /api/students/<id>/password`：{old_password?, new_password}，管理员可不带旧密码；学生本人需验证旧密码。
  - `POST /api/admin/students/<id>/reset_password`：管理员重置学生密码，生成并返回临时密码（生产建议通过邮件发送）。

开发任务建议与注意（对应 1–11 项）
1) 密码哈希：已采用 passlib pbkdf2_sha256。若需切换 bcrypt，请提供迁移策略（72 字节限制）并编写兼容迁移/回滚脚本。
2) 前端实时校验：在 `static/js` 新增通用校验（年龄 1–100、学号正整数、必填等），提交前阻断；后端仍保留 pydantic 校验。
3) CSRF：已启用并在 `@validate_json` 中默认校验。新写接口无需重复手写，只要使用装饰器即可。
4) 密码修改/重置：已提供独立接口；`PUT /api/students/<id>` 不处理密码字段，请勿在该接口混入密码逻辑。
5) 成绩外键校验：已在 POST/PUT 中实现。新增相似写接口时按此模式先校验外键。
6) 统计接口：建议新增 `/api/statistics/...`，返回平均/最大/最小/区间分布/排名等；前端使用 ECharts 或 Chart.js 可视化。
7) UX：替换 `alert()` 为 Toast/模态框；提交态增加按钮禁用+Spinner，防止重复提交。
8) 架构重构：将 `app.py` 拆分为 `app/` 包（routes/models/db/utils）；先迁移单个功能模块并保持 API 不变。
9) 数据库层：考虑 SQLAlchemy 或连接池；统一 SQL 构建并集中在 `db.py`；避免在路由中直接拼接表名/列名。
10) 配置与日志：把 DB 凭据改为环境变量（.env），新增结构化日志（INFO/ERROR 到文件）；避免输出敏感信息。
11) 测试与 CI：已引入 pytest（`tests/test_smoke.py`）。建议新增负面用例（重复添加、越界分数、未登录/缺 CSRF 等），并添加 GitHub Actions 运行 pytest。

运行/测试（本地）
- 启动服务（开发）：
  - Windows PowerShell（示例）：
    - 可选：创建并激活虚拟环境
    - 安装依赖：`pip install -r WebScoreManager/requirements.txt`
    - 运行：`python WebScoreManager/app.py`
- 端到端测试：
  - 先确保服务运行在 `http://127.0.0.1:5000`
  - 运行 pytest：`pytest WebScoreManager/tests/test_smoke.py`

编辑/贡献规则（对自动补全重要）
- 不要提交真实数据库凭据；示例凭据仅出现在注释并明确标注“示例”。
- 新增写接口时：定义 pydantic 模型 → 使用 `@validate_json(Model)` → 在函数体使用 `request.parsed` → 如涉及外键，先校验存在性。
- 修改身份/安全逻辑时：同时更新测试用例（pytest）与文档（README/Copilot 指南）。

遗留模块提示（根目录）
- `import pymysql.py`、`sc` 文件名含空格/无扩展名，打开/修改请使用绝对路径（示例：`d:/桌面/School_db/import pymysql.py`）。
- 其中包含简易 `execute_sql(sql, params=None)` 示例代码（pymysql）。不建议在主应用中直接依赖这些遗留文件。

如需我补充 CI、统计接口、前端校验或项目重构的详细步骤，请在 Issue/PR 中标注相应任务，我会按上述约定实施并同步更新本指南。

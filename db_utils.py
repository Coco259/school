# db_utils.py
import pymysql

def get_conn():
    """获取数据库连接"""
    return pymysql.connect(
        host='localhost',
        user='root',
        password='y210093',
        database='school_db',
        charset='utf8mb4'
    )

def execute(sql, params=None):
    """执行SQL（增删改），优先使用参数化以避免注入风险。"""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)
        conn.commit()  # 提交事务
        return cursor.rowcount  # 返回受影响的行数
    except Exception as e:
        conn.rollback()  # 出错回滚
        print(f"SQL执行失败：{e}")
        return -1
    finally:
        cursor.close()
        conn.close()

def query(sql, params=None):
    """执行查询SQL（查），统一走参数化查询。"""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)
        return cursor.fetchall()  # 返回查询结果（元组列表）
    except Exception as e:
        print(f"查询失败：{e}")
        return None
    finally:
        cursor.close()
        conn.close()
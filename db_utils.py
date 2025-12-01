# db_utils.py
import os
from collections.abc import Mapping
from contextlib import contextmanager
from queue import Queue
from typing import Any, Iterable, Optional, Sequence

import pymysql


class DatabaseError(RuntimeError):
    """数据库操作失败时抛出。"""


def _get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


_CONN_ARGS = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "y210093"),  # 示例默认值
    "database": os.getenv("DB_NAME", "school_db"),
    "charset": os.getenv("DB_CHARSET", "utf8mb4"),
    "autocommit": False,
}

_POOL_SIZE = _get_env_int("DB_POOL_SIZE", 5)
_POOL: Queue[pymysql.connections.Connection] = Queue(maxsize=_POOL_SIZE)


def _create_connection() -> pymysql.connections.Connection:
    conn = pymysql.connect(**_CONN_ARGS)
    conn.ping(reconnect=True)
    return conn


def get_conn() -> pymysql.connections.Connection:
    if not _POOL.empty():
        conn = _POOL.get()
        try:
            conn.ping(reconnect=True)
        except pymysql.MySQLError:
            conn.close()
            conn = _create_connection()
    else:
        conn = _create_connection()
    return conn


def release_conn(conn: Optional[pymysql.connections.Connection]) -> None:
    if conn is None:
        return
    if conn.open and not _POOL.full():
        _POOL.put(conn)
    else:
        conn.close()


@contextmanager
def _managed_cursor(write: bool) -> Any:
    conn = get_conn()
    cursor = conn.cursor()
    try:
        yield cursor
        if write:
            conn.commit()
    except Exception as exc:  # pragma: no cover - rethrow retains stack
        conn.rollback()
        raise DatabaseError(str(exc)) from exc
    finally:
        cursor.close()
        release_conn(conn)


def _prepare_params(
    sql: str,
    params: Optional[Sequence[Any] | Mapping[str, Any]],
) -> Sequence[Any] | Mapping[str, Any]:
    placeholders = sql.count("%s")
    if placeholders == 0:
        return params or ()
    if params is None:
        raise DatabaseError("参数化 SQL 必须提供 params")
    if isinstance(params, Mapping):
        return params
    if not isinstance(params, Sequence):
        raise DatabaseError("params 需为序列或映射")
    if len(params) != placeholders:
        raise DatabaseError("参数个数与占位符不匹配")
    return params


def execute(
    sql: str,
    params: Optional[Sequence[Any] | Mapping[str, Any]] = None,
) -> int:
    safe_params = _prepare_params(sql, params)
    with _managed_cursor(write=True) as cursor:
        cursor.execute(sql, safe_params)
        return cursor.rowcount


def executemany(sql: str, param_list: Iterable[Sequence[Any]]) -> int:
    batches = list(param_list)
    if not batches:
        return 0
    placeholders = sql.count("%s")
    if placeholders > 0 and any(len(item) != placeholders for item in batches):
        raise DatabaseError("参数个数与占位符不匹配")
    with _managed_cursor(write=True) as cursor:
        cursor.executemany(sql, batches)
        return cursor.rowcount


def query(
    sql: str,
    params: Optional[Sequence[Any] | Mapping[str, Any]] = None,
) -> Sequence[tuple[Any, ...]]:
    safe_params = _prepare_params(sql, params)
    with _managed_cursor(write=False) as cursor:
        cursor.execute(sql, safe_params)
        return cursor.fetchall()


def fetch_one(
    sql: str,
    params: Optional[Sequence[Any] | Mapping[str, Any]] = None,
) -> Optional[tuple[Any, ...]]:
    safe_params = _prepare_params(sql, params)
    with _managed_cursor(write=False) as cursor:
        cursor.execute(sql, safe_params)
        return cursor.fetchone()


def transaction(
    operations: Iterable[tuple[str, Optional[Sequence[Any] | Mapping[str, Any]]]],
) -> None:
    with _managed_cursor(write=True) as cursor:
        for sql, params in operations:
            safe_params = _prepare_params(sql, params)
            cursor.execute(sql, safe_params)
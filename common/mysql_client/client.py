# -*- coding:utf-8 -*-
"""作用：提供支持参数化SQL、事务回滚和安全关闭的MySQL客户端。"""

import pymysql


class MysqlClient:
    """封装轻量级MySQL查询，保留原有方法名以兼容历史项目。"""

    def __init__(
        self,
        host,
        port,
        username,
        password,
        dbname,
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=None,
        **connect_kwargs,
    ):
        connection_options = dict(
            host=host,
            port=int(port),
            user=username,
            password=password,
            db=dbname,
            charset=charset,
            cursorclass=cursorclass,
        )
        if connect_timeout is not None:
            connection_options['connect_timeout'] = connect_timeout
        connection_options.update(connect_kwargs)
        self.conn = pymysql.connect(**connection_options)

    def _execute_sql(self, sql, params=None, always_fetch=False):
        self.conn.ping(reconnect=True)
        try:
            with self.conn.cursor() as cursor:
                affected_rows = cursor.execute(sql, params)
                result = (
                    cursor.fetchall()
                    if cursor.description or always_fetch
                    else affected_rows
                )
            self.conn.commit()
            return result
        except Exception:
            self.conn.rollback()
            raise

    def execute_sql(self, sql, params=None):
        """执行参数化SQL；查询返回结果集，写操作返回影响行数。"""
        return self._execute_sql(sql, params)

    def executeSQL(self, sql, params=None):
        """兼容历史调用：任何SQL都执行fetchall并返回结果集。"""
        return self._execute_sql(sql, params, always_fetch=True)

    def execute_many(self, query, values, batch_size=1000):
        """分批执行参数化写操作，并在全部成功后统一提交事务。"""
        if batch_size <= 0:
            raise ValueError('batch_size必须大于0')
        value_list = list(values)
        if not value_list:
            return 0

        self.conn.ping(reconnect=True)
        affected_rows = 0
        try:
            with self.conn.cursor() as cursor:
                for index in range(0, len(value_list), batch_size):
                    affected_rows += cursor.executemany(
                        query,
                        value_list[index:index + batch_size],
                    )
            self.conn.commit()
            return affected_rows
        except Exception:
            self.conn.rollback()
            raise

    def executeMany(self, query, values):
        """兼容历史调用：每1000条提交一次并保持无返回值。"""
        value_list = list(values)
        if not value_list:
            return None

        self.conn.ping(reconnect=True)
        try:
            with self.conn.cursor() as cursor:
                for index in range(0, len(value_list), 1000):
                    cursor.executemany(query, value_list[index:index + 1000])
                    self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        return None

    def close(self):
        self.conn.close()

    def closeAll(self):
        """兼容历史调用，请优先使用close。"""
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

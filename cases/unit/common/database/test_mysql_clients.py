"""作用：验证MySQL客户端的参数化执行、事务回滚和SQLAlchemy 2.x兼容性。"""

import pytest

from common.mysql_client.client import MysqlClient
from common.sqlalchemy_tools.sqlalchemy_mysql_tool import SQLAlchemyMysqlTool
from common.sqlalchemy_tools.sqlalchemy_mysql_tool import SQLAlchemy_Mysql_Tool


pytestmark = pytest.mark.unit


class FakeCursor:
    def __init__(self, fail=False, has_result=True):
        self.fail = fail
        self.description = ('id',) if has_result else None
        self.execute_calls = []
        self.executemany_calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, sql, params=None):
        self.execute_calls.append((sql, params))
        if self.fail:
            raise RuntimeError('database error')
        return 1

    def executemany(self, query, values):
        self.executemany_calls.append((query, values))
        if self.fail:
            raise RuntimeError('database error')
        return len(values)

    def fetchall(self):
        return [{'id': 1}]


class FakeConnection:
    def __init__(self, cursor):
        self.test_cursor = cursor
        self.commit_count = 0
        self.rollback_count = 0
        self.closed = False

    def ping(self, reconnect=True):
        assert reconnect is True

    def cursor(self):
        return self.test_cursor

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1

    def close(self):
        self.closed = True


class TestMysqlClient:
    def test_executes_parameterized_query_and_commits(self, monkeypatch):
        """验证查询参数单独传递，并在成功后提交事务。"""
        connection = FakeConnection(FakeCursor())
        monkeypatch.setattr(
            'common.mysql_client.client.pymysql.connect',
            lambda **kwargs: connection,
        )

        with MysqlClient('localhost', 3306, 'user', 'password', 'test') as client:
            result = client.execute_sql(
                'select * from users where id=%s',
                (1,),
            )

        assert result == [{'id': 1}]
        assert connection.test_cursor.execute_calls == [
            ('select * from users where id=%s', (1,))
        ]
        assert connection.commit_count == 1
        assert connection.rollback_count == 0
        assert connection.closed is True

    def test_keeps_legacy_connection_defaults_and_return_value(self, monkeypatch):
        """验证旧默认字符集和executeSQL结果集返回语义保持兼容。"""
        connection = FakeConnection(FakeCursor(has_result=False))
        captured_options = {}

        def fake_connect(**kwargs):
            captured_options.update(kwargs)
            return connection

        monkeypatch.setattr(
            'common.mysql_client.client.pymysql.connect',
            fake_connect,
        )
        client = MysqlClient('localhost', 3306, 'user', 'password', 'test')

        result = client.executeSQL('update users set enabled=%s', (True,))

        assert result == [{'id': 1}]
        assert captured_options['charset'] == 'utf8'
        assert 'connect_timeout' not in captured_options
        client.close()

    def test_rolls_back_when_query_fails(self, monkeypatch):
        """验证数据库执行异常会回滚并保留原始异常。"""
        connection = FakeConnection(FakeCursor(fail=True))
        monkeypatch.setattr(
            'common.mysql_client.client.pymysql.connect',
            lambda **kwargs: connection,
        )
        client = MysqlClient('localhost', 3306, 'user', 'password', 'test')

        with pytest.raises(RuntimeError, match='database error'):
            client.execute_sql('update users set enabled=%s', (True,))

        assert connection.commit_count == 0
        assert connection.rollback_count == 1
        client.close()

    def test_execute_many_commits_once_after_all_batches(self, monkeypatch):
        """验证批量写入按批执行，但只在全部成功后提交一次。"""
        connection = FakeConnection(FakeCursor(has_result=False))
        monkeypatch.setattr(
            'common.mysql_client.client.pymysql.connect',
            lambda **kwargs: connection,
        )
        client = MysqlClient('localhost', 3306, 'user', 'password', 'test')

        affected_rows = client.execute_many(
            'insert into users(id) values(%s)',
            [(1,), (2,), (3,)],
            batch_size=2,
        )

        assert affected_rows == 3
        assert len(connection.test_cursor.executemany_calls) == 2
        assert connection.commit_count == 1
        client.close()

    def test_execute_many_legacy_method_commits_each_batch_and_returns_none(
        self,
        monkeypatch,
    ):
        """验证旧批量方法保持分批提交和无返回值语义。"""
        connection = FakeConnection(FakeCursor(has_result=False))
        monkeypatch.setattr(
            'common.mysql_client.client.pymysql.connect',
            lambda **kwargs: connection,
        )
        client = MysqlClient('localhost', 3306, 'user', 'password', 'test')
        values = [(index,) for index in range(1001)]

        result = client.executeMany('insert into users(id) values(%s)', values)

        assert result is None
        assert len(connection.test_cursor.executemany_calls) == 2
        assert connection.commit_count == 2
        client.close()


class TestSQLAlchemyMysqlTool:
    def test_encodes_special_characters_in_connection_url(self):
        """验证密码中的特殊字符不会破坏MySQL连接URL。"""
        tool = SQLAlchemyMysqlTool(
            host='localhost',
            port=3306,
            username='test_user',
            password='p@ss/word',
            db='automation_test',
        )

        rendered_url = tool.url.render_as_string(hide_password=False)

        assert 'p%40ss%2Fword' in rendered_url
        assert 'charset=utf8mb4' in rendered_url
        tool.close()

    def test_accepts_legacy_encoding_keyword(self):
        """验证新类接收旧encoding关键字且不会传给create_engine。"""
        tool = SQLAlchemyMysqlTool(
            host='localhost',
            port=3306,
            username='test_user',
            password='password',
            db='automation_test',
            encoding='utf8',
        )

        assert 'charset=utf8' in tool.url.render_as_string()
        tool.close()

    def test_legacy_class_returns_scoped_session_proxy(self):
        """验证旧类名继续返回历史scoped_session代理对象。"""
        tool = SQLAlchemy_Mysql_Tool(
            host='localhost',
            port=3306,
            username='test_user',
            password='password',
            db='automation_test',
        )

        assert tool.get_session() is tool._session_factory
        assert 'charset=utf8' in tool.url.render_as_string()
        tool.close()

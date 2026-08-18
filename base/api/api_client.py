"""作用：提供可由项目配置创建的通用API测试客户端。"""

import configparser
import os
from pathlib import Path

from common.http_client.request_client import DoRequest


class APIClientCleanupError(RuntimeError):
    """所有API客户端尝试关闭后，汇总仍然发生的关闭异常。"""

    def __init__(self, errors):
        self.errors = tuple(errors)
        message = '; '.join(str(error) for error in self.errors)
        super().__init__('API客户端关闭失败:%s' % message)


class APIClient:
    """封装通用HTTP请求客户端，避免每个API项目重复创建客户端类。"""

    def __init__(
        self,
        base_url,
        timeout=30,
        verify=True,
        max_retries=2,
        pool_connections=10,
        pool_maxsize=10,
        decode_errors='strict',
    ):
        normalized_url = base_url.strip().rstrip('/')
        if not normalized_url.startswith(('http://', 'https://')):
            raise ValueError('API base_url必须以http://或https://开头')
        self.request = DoRequest(
            normalized_url,
            timeout=timeout,
            verify=verify,
            max_retries=max_retries,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            decode_errors=decode_errors,
        )

    @classmethod
    def from_config(cls, config_file_path, base_url_env=None):
        """从配置文件创建客户端，并允许环境变量覆盖服务地址。"""
        config_path = Path(config_file_path)
        if not config_path.is_file():
            raise FileNotFoundError('API配置文件不存在:%s' % config_path)

        config = configparser.ConfigParser()
        loaded_files = config.read(config_path, encoding='utf-8')
        if not loaded_files:
            raise FileNotFoundError('API配置文件无法读取:%s' % config_path)

        base_url = os.getenv(base_url_env) if base_url_env else None
        if not base_url:
            base_url = config.get('servers', 'url')
        return cls(
            base_url,
            timeout=config.getfloat('http', 'timeout', fallback=30),
            verify=config.getboolean('http', 'verify', fallback=True),
            max_retries=config.getint('http', 'max_retries', fallback=2),
            pool_connections=config.getint('http', 'pool_connections', fallback=10),
            pool_maxsize=config.getint('http', 'pool_maxsize', fallback=10),
            decode_errors=config.get('http', 'decode_errors', fallback='strict'),
        )

    def close(self):
        """关闭底层HTTP会话。"""
        self.request.closeSession()


class APIClientFactory:
    """按测试或角色创建彼此隔离的API客户端，并集中释放资源。"""

    def __init__(self, config_file_path, base_url_env=None):
        self.config_file_path = config_file_path
        self.base_url_env = base_url_env
        self._clients = []

    def create(self, headers=None, cookies=None, auth_provider=None):
        """创建全新Session，可按角色设置独立Header和Cookie。"""
        client = APIClient.from_config(
            self.config_file_path,
            base_url_env=self.base_url_env,
        )
        if headers:
            client.request.setHeaders(headers)
        if cookies:
            client.request.setCookies(cookies)
        if auth_provider is not None:
            client.request.set_auth_provider(auth_provider)
        self._clients.append(client)
        return client

    def close_all(self):
        """反向关闭全部客户端，单个失败不会阻止其余资源释放。"""
        errors = []
        while self._clients:
            client = self._clients.pop()
            try:
                client.close()
            except Exception as exc:
                errors.append(exc)
        if errors:
            raise APIClientCleanupError(errors)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.close_all()
        except APIClientCleanupError as cleanup_error:
            if exc_value is None:
                raise
            exc_value.add_note(str(cleanup_error))
        return False

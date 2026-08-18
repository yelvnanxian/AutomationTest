"""作用：提供可由项目配置创建的通用API测试客户端。"""

import configparser
import os
from pathlib import Path

from common.http_client.request_client import DoRequest


class APIClient:
    """封装通用HTTP请求客户端，避免每个API项目重复创建客户端类。"""

    def __init__(self, base_url):
        normalized_url = base_url.strip().rstrip('/')
        if not normalized_url.startswith(('http://', 'https://')):
            raise ValueError('API base_url必须以http://或https://开头')
        self.request = DoRequest(normalized_url)

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
        return cls(base_url)

    def close(self):
        """关闭底层HTTP会话。"""
        self.request.closeSession()

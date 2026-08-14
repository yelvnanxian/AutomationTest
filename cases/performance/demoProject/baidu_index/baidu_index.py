"""作用：定义百度首页的Locust性能测试用户和请求任务。"""

import queue

from locust import FastHttpUser, between, task
from locust.exception import StopUser


class BaiduIndexUser(FastHttpUser):
    """以每个工作进程100次请求为上限访问百度首页。"""

    host = 'https://www.baidu.com'
    wait_time = between(0, 0)
    execution_count = 100
    request_numbers = queue.Queue()
    for request_number in range(execution_count):
        request_numbers.put_nowait(request_number)

    @task(1)
    def index(self):
        try:
            self.request_numbers.get_nowait()
        except queue.Empty:
            raise StopUser()
        self.client.get('/', name='/')

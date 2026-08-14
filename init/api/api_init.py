#-*- coding:utf8 -*-
"""作用：执行api init相关的运行前初始化。"""

from init.api.demoProject.demo_project_init import DemoProjectInit

def api_init():
    """
    初始化必要的数据
    :return:
    """

    # 初始化demoProject项目基础数据
    DemoProjectInit().init()

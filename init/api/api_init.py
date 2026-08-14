#-*- coding:utf8 -*-
"""作用：执行api init相关的运行前初始化。"""

# 创建时间 2018/01/19 22:36
from init.api.demoProject.demoProjectInit import DemoProjectInit

def api_init():
    """
    初始化必要的数据
    :return:
    """

    # 初始化demoProject项目基础数据
    DemoProjectInit().init()

#-*- coding:utf8 -*-
"""作用：执行android init相关的运行前初始化。"""

# 创建时间 2018/01/19 22:36
from init.app_ui.android.demoProject.demoProjectInit import DemoProjectInit

def android_init():
    """
    初始化android项目必要的数据
    :return:
    """
    # demoProject项目初始化
    DemoProjectInit().init()

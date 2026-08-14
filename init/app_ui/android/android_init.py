#-*- coding:utf8 -*-
"""作用：执行android init相关的运行前初始化。"""

from init.app_ui.android.demoProject.demo_project_init import DemoProjectInit

def android_init():
    """
    初始化android项目必要的数据
    :return:
    """
    # demoProject项目初始化
    DemoProjectInit().init()

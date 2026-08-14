#-*- coding:utf8 -*-
"""作用：执行web ui init相关的运行前初始化。"""

from init.java.java_maven_init import java_maven_init
from init.web_ui.demoProject.demo_project_init import DemoProjectInit

def web_ui_init():
    """
    初始化必要的数据
    :return:
    """
    # 初始化java依赖的libs
    java_maven_init()
    # demoProject项目初始化
    DemoProjectInit().init()

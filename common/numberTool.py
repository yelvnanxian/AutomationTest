#!-*- coding:utf8 -*-
"""作用：提供numberTool相关的通用工具能力。"""

# 创建时间 2018/01/19 22:36
import re

class NumberTool:

    @classmethod
    def isPhoneAvailable(cls,mobile):
        """
        判断手机号是否合法
        :param mobile:
        :return:
        """
        mobile=str(mobile)
        regular=re.compile(r'^1[3578]\d{9}$|^14[56789]\d{8}$')
        if regular.match(mobile):
            return True
        else:
            return False

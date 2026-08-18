"""作用：集中定义httpbin测试使用的接口路径。"""


class HttpbinEndpoints:
    """维护httpbin接口路径，避免测试用例直接拼接URL。"""

    GET = '/get'
    POST = '/post'
    HEADERS = '/headers'
    STATUS = '/status/{status_code}'
    BASIC_AUTH = '/basic-auth/{username}/{password}'

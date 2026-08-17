"""作用：集中定义demoProject搜索接口的请求路径。"""


class SearchEndpoints:
    """维护搜索模块使用的接口路径，避免路径散落在测试用例中。"""

    INDEX = '/'
    SEARCH = '/s'

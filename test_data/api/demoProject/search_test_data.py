"""作用：集中维护demoProject搜索接口的输入和预期结果。"""


INDEX_EXPECTED_STATUS = 200

SEARCH_CASES = (
    {
        'case_name': '普通英文关键字',
        'keyword': 'apitest',
        'expected_status': 200,
    },
    {
        'case_name': '中文关键字',
        'keyword': '自动化测试',
        'expected_status': 200,
    },
)

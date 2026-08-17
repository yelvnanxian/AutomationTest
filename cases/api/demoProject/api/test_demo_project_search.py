"""作用：验证demoProject首页和搜索接口的响应状态。"""

import pytest

from common.hamcrest.hamcrest import assert_that
from test_data.api.demoProject.search_test_data import (
    INDEX_EXPECTED_STATUS,
    SEARCH_CASES,
)


class TestSearch:
    def test_get_index(self, search_service):
        """验证首页接口能够正常响应。"""
        response = search_service.open_index()
        assert_that(response.status_code).is_equal_to(INDEX_EXPECTED_STATUS)

    @pytest.mark.search_kw
    @pytest.mark.parametrize(
        'case_data',
        SEARCH_CASES,
        ids=[case['case_name'] for case in SEARCH_CASES],
    )
    def test_search_keyword(self, search_service, case_data):
        """验证不同搜索关键字都能获得正常响应。"""
        response = search_service.search(case_data['keyword'])
        assert_that(response.status_code).is_equal_to(case_data['expected_status'])

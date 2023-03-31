import os
from tap_tester.base_suite_tests.pagination_test import PaginationTest
from datetime import datetime as dt
from datetime import timedelta

from base import ZoomBase


class ZoomPaginationTest(PaginationTest, ZoomBase):
    """Zoom pagination test implementation """


    @staticmethod
    def name():
        return "tt_ga4_pagination"


    def get_page_limit_for_stream(self, stream):
        return self.PAGE_SIZE


    def streams_to_test(self):
        return set(self.expected_metadata().keys())
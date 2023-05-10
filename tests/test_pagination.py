from tap_tester.base_suite_tests.pagination_test import PaginationTest
from base import ZoomBase


class ZoomPaginationTest(PaginationTest, ZoomBase):
    """Zoom pagination test implementation """


    @staticmethod
    def name():
        return "tt_zoom_pagination"


    def get_page_limit_for_stream(self, stream):
        return 10


    def streams_to_test(self):
        # Skipping meetings & it's child streams due to large number of API calls which times out CircleCI
        # Added defect TDL-22941 for excluding 'webinars' stream for this test.
        return {'webinar_polls', 'webinar_registrants', 'users', 'webinar_questions', 'webinar_tracking_sources'}

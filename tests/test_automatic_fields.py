from tap_tester.base_suite_tests.automatic_fields_test import MinimumSelectionTest
from base import ZoomBase


class ZoomMinimumSelectionTest(MinimumSelectionTest, ZoomBase):
    """Standard Automatic Fields Test"""

    @staticmethod
    def name():
        return "tt_zoom_auto"

    def streams_to_test(self):
        # Skipping meetings & it's child streams due to large number of API calls which times out CircleCI
        return {'webinar_polls', 'webinar_registrants', 'users', 'webinar_questions', 'webinar_tracking_sources'}

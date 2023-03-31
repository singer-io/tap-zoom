from tap_tester.base_suite_tests.automatic_fields_test import MinimumSelectionTest

from base import ZoomBase


class GA4MinimumSelectionTest(MinimumSelectionTest, ZoomBase):
    """Standard Automatic Fields Test"""

    @staticmethod
    def name():
        return "tt_zoom_auto"

    def streams_to_test(self):
        return set(self.expected_metadata().keys())

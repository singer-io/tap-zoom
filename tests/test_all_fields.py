"""
Test that with no fields selected for a stream automatic fields are still replicated
"""

from tap_tester import runner, menagerie, connections
from tap_tester.base_suite_tests.all_fields_test import AllFieldsTest
from tap_tester.logger import LOGGER
from base import ZoomBase

class ZoomAllFieldsTest(AllFieldsTest, ZoomBase):
    """Test that with no fields selected for a stream automatic fields are still replicated"""


    @staticmethod
    def name():
        return "tt_zoom_all_fields_test"

    def streams_to_test(self):
        return set(self.expected_metadata().keys())

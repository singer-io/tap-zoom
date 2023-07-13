from tap_tester.base_suite_tests.discovery_test import DiscoveryTest
from base import ZoomBase


class ZoomDiscoveryTest(DiscoveryTest, ZoomBase):
    """Standard Discovery Test"""

    @staticmethod
    def name():
        return "tt_zoom_discovery"

    def streams_to_test(self):
        # return set(self.expected_metadata().keys())
        return self.expected_stream_names()

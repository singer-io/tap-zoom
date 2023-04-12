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
        return {'webinars', 'webinar_polls'}
    
    def test_all_fields_for_streams_are_replicated(self):
        keys_to_remove = set()
        for stream in self.streams_to_test():
            with self.subTest(stream=stream):
                stream_name = self.get_stream_name(stream)
                if stream == 'webinars':
                    keys_to_remove = {'occurences', 'tracking_fields', 'recurrence'}

                # gather expectations
                expected_all_keys = self.selected_fields.get(stream_name, set()) - keys_to_remove

                # gather results
                actual_all_keys_per_record = [set(message['data'].keys()) for message in
                                              self.get_upsert_messages_for_stream(self.synced_records, stream_name)]

                for actual_all_keys in actual_all_keys_per_record:
                    self.assertSetEqual(expected_all_keys, actual_all_keys)

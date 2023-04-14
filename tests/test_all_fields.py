from tap_tester.base_suite_tests.all_fields_test import AllFieldsTest
from base import ZoomBase


class ZoomAllFieldsTest(AllFieldsTest, ZoomBase):
    """Test that with no fields selected for a stream automatic fields are still replicated"""

    @staticmethod
    def name():
        return "tt_zoom_all_fields_test"

    def streams_to_test(self):
        # Skipping meetings & it's child streams as it has huge amount of data which times out CircleCI
        return {'webinars', 'webinar_polls', 'webinar_registrants', 'users', 'webinar_questions', 'webinar_tracking_sources'}
    
    def test_all_fields_for_streams_are_replicated(self):
        keys_to_remove = set()
        for stream in self.streams_to_test():
            with self.subTest(stream=stream):
                stream_name = self.get_stream_name(stream)
                if stream == 'webinars':
                    keys_to_remove = {'record_file_id', 'tracking_fields'}
                elif stream == 'users':
                    keys_to_remove = {'plan_united_type', 'custom_attributes', 'im_group_ids'}
                elif stream == 'webinar_tracking_sources':
                    keys_to_remove = {'registration_count'}

                # gather expectations
                expected_all_keys = self.selected_fields.get(stream_name, set()) - keys_to_remove

                # gather results
                actual_all_keys_per_record = [set(message['data'].keys()) for message in
                                              self.get_upsert_messages_for_stream(self.synced_records, stream_name)]

                actual_all_keys = set()
                for record_keys in actual_all_keys_per_record:
                    actual_all_keys.update(record_keys)
                self.assertSetEqual(expected_all_keys, actual_all_keys)

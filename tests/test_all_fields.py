from tap_tester.base_suite_tests.all_fields_test import AllFieldsTest
from base import ZoomBase


class ZoomAllFieldsTest(AllFieldsTest, ZoomBase):
    """Test that with no fields selected for a stream automatic fields are still replicated"""

    @staticmethod
    def name():
        return "tt_zoom_all_fields_test"

    def streams_to_test(self):
        # Skipping meetings & it's child streams due to large number of API calls which times out CircleCI
        return {'webinars', 'webinar_polls', 'webinar_registrants', 'users', 'webinar_questions', 'webinar_tracking_sources'}
    
    # Overriding test_all_fields_for_streams_are_replicated() method from AllFieldsTest
    def test_all_fields_for_streams_are_replicated(self):
        keys_to_remove = set()

        # Skipping fields as per the stream for which there is no data available
        MISSING_FIELDS = {
            'users': {'plan_united_type', 'custom_attributes', 'im_group_ids'},
            'webinars': {'record_file_id', 'tracking_fields'},
            'webinar_tracking_sources': {'registration_count'}
        }
        for stream in self.streams_to_test():
            with self.subTest(stream=stream):
                # gather expectations
                expected_all_keys = self.selected_fields.get(stream, set()) - MISSING_FIELDS.get(stream, set())

                # gather results
                fields_replicated = self.actual_fields.get(stream, set())

                # verify that all fields are sent to the target
                # test the combination of all records
                self.assertSetEqual(fields_replicated, expected_all_keys,
                                    logging=f"verify all fields are replicated for stream {stream}")

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
        # Skipping meetings & it's child streams as it has huge amount of data which times out CircleCI
        return {'webinars', 'webinar_polls', 'webinar_registrants', 'users', 'webinar_questions', 'webinar_tracking_sources'}


    def test_no_duplicate_records(self):
        """Test that records for each stream are not duplicated between pages"""
        for stream in self.streams_to_test():
            with self.subTest(stream=stream):
                stream_name = self.get_stream_name(stream)

                # gather expectations
                expected_primary_keys = self.expected_primary_keys().get(stream_name)

                # gather results
                primary_keys_list = [tuple([message.get('data').get(expected_pk) for expected_pk in expected_primary_keys])
                                     for message in self.get_upsert_messages_for_stream(self.synced_records, stream_name)]

                primary_keys_set = set(primary_keys_list)
                if stream == 'webinars':
                    primary_keys_set = primary_keys_list

                self.assertEqual(len(primary_keys_set), self.record_count_by_stream.get(stream_name))

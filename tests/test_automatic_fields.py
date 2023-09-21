from tap_tester.base_suite_tests.automatic_fields_test import MinimumSelectionTest
from base import ZoomBase


class ZoomMinimumSelectionTest(MinimumSelectionTest, ZoomBase):
    """Standard Automatic Fields Test"""

    @staticmethod
    def name():
        return "tt_zoom_auto"

    def expected_automatic_fields(self, stream=None):
        """
        return a dictionary with key of table name
        and value as a set of automatic fields
        """
        MISSING_FIELDS = {
            "webinar_polls": {'title', 'status', 'poll_type', 'anonymous', 'questions'},
            "webinar_tracking_sources": {'visitor_count', 'source_name', 'tracking_url'},
            "users": {'group_ids', 'timezone', 'verified', 'pmi', 'display_name', 'user_created_at',
                      'last_login_time', 'type', 'email', 'status', 'employee_unique_id', 'role_id',
                      'last_name', 'first_name', 'last_client_version', 'dept'},
            "webinar_questions": {'questions', 'custom_questions'},
            "webinar_registrants": {'address', 'comments', 'job_title', 'city', 'join_url', 'industry',
                                    'org', 'role_in_purchase_process', 'country', 'zip', 'create_time',
                                    'email', 'state', 'status', 'last_name', 'purchasing_time_frame',
                                    'no_of_employees', 'phone', 'first_name', 'custom_questions'}
        }
        automatic_fields = {
            table: properties.get(self.PRIMARY_KEYS, set())
            | properties.get(self.REPLICATION_KEYS, set())
            for table, properties in self.expected_metadata().items()}
        if not stream:
            return automatic_fields
        return automatic_fields[stream] | MISSING_FIELDS[stream]

    def streams_to_test(self):
        # Skipping meetings & it's child streams due to large number of API calls which times out CircleCI
        return {'webinar_polls', 'webinar_registrants', 'users', 'webinar_questions', 'webinar_tracking_sources'}

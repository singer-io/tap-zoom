"""
Setup expectations for test sub classes
Run discovery for as a prerequisite for most tests
"""
import os
from datetime import datetime as dt
from datetime import timedelta

from tap_tester import connections, menagerie, runner, LOGGER
from tap_tester.base_suite_tests.base_case import BaseCase


class ZoomBase(BaseCase):
    """
    Setup expectations for test sub classes.
    Metadata describing streams.

    A bunch of shared methods that are used in tap-tester tests.
    Shared tap-specific methods (as needed).
    """


    REPLICATION_KEY_FORMAT = "%Y-%m-%dT00:00:00.000000Z"
    BOOKMARK_FORMAT = "%Y-%m-%d"
    PAGE_SIZE = 100000
    start_date = ""


    @staticmethod
    def tap_name():
        """The name of the tap"""
        return "tap-zoom"


    @staticmethod
    def get_type():
        """the expected url route ending"""
        return "platform.zoom"


    def get_properties(self, original: bool = True):
        """Configuration properties required for the tap."""

        return_value = {
            'client_id':os.getenv('TAP_ZOOM_CLIENT_ID'),
            'client_secret':os.getenv('TAP_ZOOM_CLIENT_SECRET'),
            'refresh_token':os.getenv('TAP_ZOOM_REFRESH_TOKEN')
        }

        return return_value


    @staticmethod
    def get_credentials():
        return {
            'client_id':os.getenv('TAP_ZOOM_CLIENT_ID'),
            'client_secret':os.getenv('TAP_ZOOM_CLIENT_SECRET'),
            'refresh_token':os.getenv('TAP_ZOOM_REFRESH_TOKEN')
        }


    def expected_metadata(self):
        """The expected streams and metadata about the streams"""

        return {
            'users': {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'meetings': {
                self.PRIMARY_KEYS: {"uuid"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'meeting_polls': {
                self.PRIMARY_KEYS: {"meeting_id", "id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'meeting_poll_results': {
                self.PRIMARY_KEYS: {"meeting_uuid", "email"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'meeting_registrants': {
                self.PRIMARY_KEYS: {"meeting_id", "id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'meeting_questions': {
                self.PRIMARY_KEYS: {"meeting_id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'report_meetings': {
                self.PRIMARY_KEYS: {"uuid"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'report_meeting_participants': {
                self.PRIMARY_KEYS: {"meeting_id", "id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'webinars': {
                self.PRIMARY_KEYS: {"uuid"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'webinar_absentees': {
                self.PRIMARY_KEYS: {"webinar_uuid", "id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'webinar_poll_results': {
                self.PRIMARY_KEYS: {"webinar_uuid", "email"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'webinar_qna_results': {
                self.PRIMARY_KEYS: {"webinar_uuid", "email"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'webinar_panelists': {
                self.PRIMARY_KEYS: {"webinar_id", "id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'webinar_registrants': {
                self.PRIMARY_KEYS: {"webinar_id", "id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'webinar_polls': {
                self.PRIMARY_KEYS: {"webinar_id", "id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'webinar_questions': {
                self.PRIMARY_KEYS: {"webinar_id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'webinar_tracking_sources': {
                self.PRIMARY_KEYS: {"webinar_id", "id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'report_webinars': {
                self.PRIMARY_KEYS: {"uuid"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
            'report_webinar_participants': {
                self.PRIMARY_KEYS: {"webinar_id", "id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
                self.RESPECTS_START_DATE: False,
            },
        }

    def expected_automatic_fields(self):
        auto_fields = {}
        for k, v in self.expected_metadata().items():
            auto_fields[k] = v.get(self.PRIMARY_KEYS, set()) | v.get(self.REPLICATION_KEYS, set())

        return auto_fields


    @classmethod
    def setUpClass(cls):
        super().setUpClass(logging="Ensuring environment variables are sourced.")
        missing_envs = [
            x for x in [
                "TAP_ZOOM_CLIENT_ID", "TAP_ZOOM_CLIENT_SECRET", "TAP_ZOOM_REFRESH_TOKEN"
            ] if os.getenv(x) is None
        ]

        if len(missing_envs) != 0:
            raise Exception("Missing environment variables: {}".format(missing_envs))


    ##########################################################################
    ### Tap Specific Methods
    ##########################################################################


    @staticmethod
    def expected_pagination_fields(): # TODO does this apply?
        return {
            "Test Report 1" : set(),
            "Audience Overview": {
                "ga:users", "ga:newUsers", "ga:sessions", "ga:sessionsPerUser", "ga:pageviews",
                "ga:pageviewsPerSession", "ga:sessionDuration", "ga:bounceRate", "ga:date",
                # "ga:pageviews",
            },
            "Audience Geo Location": set(),
            "Audience Technology": set(),
            "Acquisition Overview": set(),
            "Behavior Overview": set(),
            "Ecommerce Overview": set(),
        }



    # TODO refactor code to remove this method if possible, ga4 relic
    def get_stream_name(self, stream):
        """
        Returns the stream_name given the tap_stream_id because synced_records
        from the target output batches records by stream_name

        Since the GA4 tap_stream_id is a UUID instead of the usual case of
        tap_stream_id == stream_name, we need to get the stream_name that
        maps to tap_stream_id
        """
        stream_name=stream
        # custom_reports_names_to_ids().get(tap_stream_id, tap_stream_id)
        return stream_name 


    @staticmethod
    def select_all_streams_and_fields(conn_id, catalogs, select_all_fields: bool = True):
        """Select all streams and all fields within streams"""
        for catalog in catalogs:
            schema = menagerie.get_annotated_schema(conn_id, catalog['stream_id'])

            non_selected_properties = []
            if not select_all_fields:
                # get a list of all properties so that none are selected
                non_selected_properties = schema.get('annotated-schema', {}).get(
                    'properties', {}).keys()

            connections.select_catalog_and_fields_via_metadata(
                conn_id, catalog, schema, [], non_selected_properties)


    def perform_and_verify_table_and_field_selection(self,
                                                     conn_id,
                                                     test_catalogs,
                                                     select_all_fields=True):
        """
        Perform table and field selection based off of the streams to select
        set and field selection parameters.
        Verify this results in the expected streams selected and all or no
        fields selected for those streams.
        """


        # Select all available fields or select no fields from all testable streams
        self.select_all_streams_and_fields(
            conn_id=conn_id, catalogs=test_catalogs, select_all_fields=select_all_fields
        )

        catalogs = menagerie.get_catalogs(conn_id)

        # Ensure our selection affects the catalog
        expected_selected = [tc.get('stream_name') for tc in test_catalogs]
        for cat in catalogs:
            catalog_entry = menagerie.get_annotated_schema(conn_id, cat['stream_id'])

            # Verify all testable streams are selected
            selected = catalog_entry.get('annotated-schema').get('selected')
            print("Validating selection on {}: {}".format(cat['stream_name'], selected))
            if cat['stream_name'] not in expected_selected:
                self.assertFalse(selected, msg="Stream selected, but not testable.")
                continue # Skip remaining assertions if we aren't selecting this stream
            self.assertTrue(selected, msg="Stream not selected.")

            if select_all_fields:
                # Verify all fields within each selected stream are selected
                for field, field_props in catalog_entry.get('annotated-schema').get('properties').items():
                    field_selected = field_props.get('selected')
                    print("\tValidating selection on {}.{}: {}".format(
                        cat['stream_name'], field, field_selected))
                    self.assertTrue(field_selected, msg="Field not selected.")
            else:
                # Verify only automatic fields are selected
                expected_automatic_fields = self.expected_automatic_fields().get(cat['stream_name'])
                selected_fields = self.get_selected_fields_from_metadata(catalog_entry['metadata'])
                self.assertEqual(expected_automatic_fields, selected_fields)


    def get_sync_start_time(self, stream, bookmark):
        """
        Calculates the sync start time, with respect to the lookback window
        """
        conversion_day = dt.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None) - timedelta(days=self.lookback_window)
        bookmark_datetime = dt.strptime(bookmark, self.BOOKMARK_FORMAT)
        start_date_datetime = dt.strptime(self.start_date, self.START_DATE_FORMAT)
        return  min(bookmark_datetime, max(start_date_datetime, conversion_day))


    # TODO is this still useful now that we have get_stream_name?
    def get_record_count_by_stream(self, record_count, stream):
        count = record_count.get(stream)
        if not count:
            stream_name = self.custom_reports_names_to_ids().get(stream)
            return record_count.get(stream_name)
        return count


    def get_bookmark_value(self, state, stream):
        bookmark = state.get('bookmarks', {})
        stream_bookmark = bookmark.get(stream)
        stream_replication_key = self.expected_metadata().get(stream,set()).get('REPLICATION_KEYS')
        if stream_bookmark:
            return stream_bookmark.get(stream_replication_key)
        return None
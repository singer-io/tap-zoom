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
    PAGE_SIZE = 100000

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

    @classmethod
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

import singer
from singer import metrics, write_record
from singer.metadata import get_standard_metadata, to_list, to_map, write
from abc import ABC, abstractmethod

LOGGER = singer.get_logger()


class FullTableStream(ABC):
    """Base Class for Full Table Stream."""

    replication_method = "FULL_TABLE"
    forced_replication_method = "FULL_TABLE"
    tap_stream_id = None
    valid_replication_keys = None
    replication_key = None

    def __init__(self, client=None):
        self.client = client

    @property
    @abstractmethod
    def key_properties(self):
        """List of key properties for stream."""

    @abstractmethod
    def get_records(self):
        """Interacts with api client interaction and pagination."""

    def sync(self, state, schema, stream_metadata, transformer) :
        """Abstract implementation for `type: Full Table` stream."""
        with metrics.record_counter(self.tap_stream_id) as counter:
            for record in self.get_records():
                transformed_record = transformer.transform(record, schema, stream_metadata)
                write_record(self.tap_stream_id, transformed_record)
                counter.increment()
        return state

    @classmethod
    def get_metadata(cls, schema):
        """Returns a `dict` for generating stream metadata."""
        stream_metadata = get_standard_metadata(
            **{
                "schema": schema,
                "key_properties": cls.key_properties,
                "valid_replication_keys": cls.valid_replication_keys,
                "replication_method": cls.replication_method or cls.forced_replication_method,
            }
        )
        stream_metadata = to_map(stream_metadata)
        if cls.valid_replication_keys is not None:
            for key in cls.valid_replication_keys:
                stream_metadata = write(stream_metadata, ("properties", key), "inclusion", "automatic")
        stream_metadata = to_list(stream_metadata)
        return stream_metadata


class Users(FullTableStream) :
    """Users stream implementation"""
    path = "users"
    key_properties = ["id"]
    tap_stream_id = "users"
    ignore_zoom_error_codes = []
    ignore_http_error_codes = []

    def get_records(self) :
        """performs api querying and pagination of response."""
        params, call_next = {"page_size": 300, "page_number": 1}, True
        while call_next:
            response = self.client.get(self.path,
                                       params = params,
                                       endpoint = self.tap_stream_id,
                                       ignore_zoom_error_codes = self.ignore_zoom_error_codes,
                                       ignore_http_error_codes = self.ignore_http_error_codes) #, headers, self.api_auth_version

            # retrieve records from response.users key
            raw_records = response.get(self.tap_stream_id, [])

            # retrieve pagination from response.page_number key
            next_param = response.get("page_number", None)

            if not raw_records or not next_param:
                call_next = False

            if params["page_number"] <= response.get('page_count', 1):
                # each endpoint has a different max page size, the server will send the one that is forced
                params["page_size"] = response["page_size"]
                params["page_number"] = next_param + 1
            else:
                break

            yield from raw_records

    def prefetch_user_ids(self):
        """Helper method implemented for other streams to load all user_ids.

        eg: user ids are required to fetch meeting ids
        """
        user_ids = getattr(self.client, "shared_user_ids", [])
        if not user_ids:
            LOGGER.info("Fetching all user_ids")
            for record in self.get_records():
                try:
                    user_ids.append(record["id"])
                except KeyError:
                    LOGGER.warning("Unable to find external user ID")

            self.client.shared_user_ids = sorted(user_ids, key=lambda _: _[0])
        return user_ids


class ListMeetings(FullTableStream):
    """class for list meetings stream."""
    path = "users/{user_id}/meetings"
    tap_stream_id = "list_meetings"
    data_key = "meetings"
    key_properties = []
    ignore_zoom_error_codes = []
    ignore_http_error_codes = []

    def get_users(self):
        """Returns index for sync resuming on interruption."""
        shared_user_ids = Users(self.client).prefetch_user_ids()
        return shared_user_ids

    def get_meeting_ids(self, user_id_str) :
        """performs api querying and pagination of response."""
        params, call_next = {"page_size": 300, "page_number": 1}, True
        path = self.path.replace("{user_id}",user_id_str)
        while call_next:
            response = self.client.get(path,
                                       params = params,
                                       endpoint = self.tap_stream_id,
                                       ignore_zoom_error_codes = self.ignore_zoom_error_codes,
                                       ignore_http_error_codes = self.ignore_http_error_codes) #, headers, self.api_auth_version

            # retrieve records from response.users key
            raw_records = response.get(self.data_key, [])
            # retrieve pagination from response.page_number key
            next_param = response.get("page_number", None)

            if not raw_records or not next_param:
                call_next = False

            if params["page_number"] <= response.get('page_count', 1):
                # each endpoint has a different max page size, the server will send the one that is forced
                params["page_size"] = response["page_size"]
                params["page_number"] = next_param + 1
            else:
                break

            yield from raw_records

    def get_records(self):
        """Sync implementation for `list_meetings` stream."""
        with metrics.Timer(self.tap_stream_id, None):
            users = self.get_users()
            meeting_ids = []
            # with metrics.Counter(self.tap_stream_id) as counter:
            for user_id in users:
                for record in self.get_meeting_ids(str(user_id)):
                    try:
                        meeting_ids.append(record["id"])
                    except KeyError:
                        LOGGER.warning("Unable to find meeting IDs")
            return meeting_ids


class Meetings(FullTableStream):
    """class for meeting_polls stream."""
    path = "meetings/{meeting_id}"
    key_properties = ["uuid"]
    tap_stream_id = "meetings"
    # data_key = "meetings"
    ignore_zoom_error_codes = []
    ignore_http_error_codes = []

    def get_records(self, single_item_str):
        """performs api querying and pagination of response."""
        path = self.path.replace("{meeting_id}", single_item_str)

        response = self.client.get(path,
                                #    params = params,
                                    endpoint = self.tap_stream_id,
                                    ignore_zoom_error_codes = self.ignore_zoom_error_codes,
                                    ignore_http_error_codes = self.ignore_http_error_codes)

        raw_records = response #.get(self.data_key, [])

        if not raw_records:
            LOGGER.warning("No records found as a response")

        yield from raw_records

    def sync(self, state, schema, stream_metadata, transformer):
        """Sync implementation for `meeting_polls` stream."""
        meeting_ids = ListMeetings(self.client).get_records()

        with metrics.record_counter(self.tap_stream_id) as counter:
            for single_item in meeting_ids :
                for record in self.get_records(str(single_item)):
                    transformed_record = transformer.transform(record, schema, stream_metadata)
                    write_record(self.tap_stream_id, transformed_record)
                    counter.increment()
        return state

class MeetingPolls(FullTableStream):
    """class for meeting_polls stream."""
    path = "meetings/{meeting_id}/polls"
    key_properties = ["meeting_id", "id"]
    tap_stream_id = "meeting_polls"
    data_key = "polls"
    ignore_zoom_error_codes = []
    ignore_http_error_codes = []

    def get_records(self, single_item_str):
        """performs api querying and pagination of response."""
        path = self.path.replace("{meeting_id}", single_item_str)

        response = self.client.get(path,
                                #    params = params,
                                    endpoint = self.tap_stream_id,
                                    ignore_zoom_error_codes = self.ignore_zoom_error_codes,
                                    ignore_http_error_codes = self.ignore_http_error_codes)
        if response is None:
            response = {self.data_key : []}
        
        raw_records = response.get(self.data_key, [])

        if not raw_records:
            LOGGER.warning("No records found as a response")

        yield from raw_records

    def sync(self, state, schema, stream_metadata, transformer):
        """Sync implementation for `meeting_polls` stream."""
        meeting_ids = ListMeetings(self.client).get_records()

        with metrics.record_counter(self.tap_stream_id) as counter:
            for single_item in meeting_ids :
                for record in self.get_records(str(single_item)):
                    transformed_record = transformer.transform(record, schema, stream_metadata)
                    write_record(self.tap_stream_id, transformed_record)
                    counter.increment()
            
        return state

class MeetingRegistrants(FullTableStream):
    """class for meeting_polls stream."""
    path = "meetings/{meeting_id}/registrants"
    key_properties = ["meeting_id", "id"]
    tap_stream_id = "meeting_registrants"
    data_key = "registrants"
    ignore_zoom_error_codes = []
    ignore_http_error_codes = []

    def get_records(self, single_item_str):
        """performs api querying and pagination of response."""
        path = self.path.replace("{meeting_id}", single_item_str)
        params, call_next = {"page_size": 300, "page_number": 1}, True
        while call_next:
            response = self.client.get(path,
                                        params = params,
                                        endpoint = self.tap_stream_id,
                                        ignore_zoom_error_codes = self.ignore_zoom_error_codes,
                                        ignore_http_error_codes = self.ignore_http_error_codes)
            raw_records = response.get(self.data_key, [])

            if not raw_records:
                LOGGER.warning("No records found as a response")

            # retrieve pagination from response.page_number key
            next_param = response.get("page_number", None)

            if not raw_records or not next_param:
                call_next = False

            if params["page_number"] <= response.get('page_count', 1):
                # each endpoint has a different max page size, the server will send the one that is forced
                params["page_size"] = response["page_size"]
                params["page_number"] = next_param + 1
            else:
                break

            yield from raw_records

    def sync(self, state, schema, stream_metadata, transformer):
        """Sync implementation for `meeting_polls` stream."""
        meeting_ids = ListMeetings(self.client).get_records()

        with metrics.record_counter(self.tap_stream_id) as counter:
            for single_item in meeting_ids :
                for record in self.get_records(str(single_item)):
                    transformed_record = transformer.transform(record, schema, stream_metadata)
                    write_record(self.tap_stream_id, transformed_record)
                    counter.increment()
        return state

class MeetingQuestions(FullTableStream):
    """class for meeting_polls stream."""
    path = "meetings/{meeting_id}/registrants/questions"
    key_properties = ["meeting_id"]
    tap_stream_id = "meeting_questions"
    ignore_zoom_error_codes = [3000]
    ignore_http_error_codes = []

    def get_records(self, single_item_str):
        """performs api querying and pagination of response."""
        path = self.path.replace("{meeting_id}", single_item_str)

        response = self.client.get(path,
                                #    params = params,
                                    endpoint = self.tap_stream_id,
                                    ignore_zoom_error_codes = self.ignore_zoom_error_codes,
                                    ignore_http_error_codes = self.ignore_http_error_codes)
        raw_records = response #.get(self.data_key, [])

        if not raw_records:
            LOGGER.warning("No records found as a response")

        yield from raw_records

    def sync(self, state, schema, stream_metadata, transformer):
        """Sync implementation for `meeting_polls` stream."""
        meeting_ids = ListMeetings(self.client).get_records()
        meeting_ids_len = len(meeting_ids)

        with metrics.record_counter(self.tap_stream_id) as counter:
            for single_item in meeting_ids :
                for record in self.get_records(str(single_item)):
                    transformed_record = transformer.transform(record, schema, stream_metadata)
                    write_record(self.tap_stream_id, transformed_record)
                    counter.increment()
        return state

class ReportMeetings(FullTableStream):
    """class for meeting_polls stream."""
    path = "report/meetings/{meeting_id}"
    key_properties = ["uuid"]
    tap_stream_id = "report_meetings"
    ignore_zoom_error_codes = []
    ignore_http_error_codes = []

    def get_records(self, single_item_str):
        """performs api querying and pagination of response."""
        path = self.path.replace("{meeting_id}", single_item_str)

        response = self.client.get(path,
                                #    params = params,
                                    endpoint = self.tap_stream_id,
                                    ignore_zoom_error_codes = self.ignore_zoom_error_codes,
                                    ignore_http_error_codes = self.ignore_http_error_codes)
        raw_records = response #.get(self.data_key, [])

        if not raw_records:
            LOGGER.warning("No records found as a response")

        yield from raw_records

    def sync(self, state, schema, stream_metadata, transformer):
        """Sync implementation for `meeting_polls` stream."""
        meeting_ids = ListMeetings(self.client).get_records()

        with metrics.record_counter(self.tap_stream_id) as counter:
            for single_item in meeting_ids :
                for record in self.get_records(str(single_item)):
                    transformed_record = transformer.transform(record, schema, stream_metadata)
                    write_record(self.tap_stream_id, transformed_record)
                    counter.increment()
        return state

class ReportMeetingParticipants(FullTableStream):
    """class for meeting_polls stream."""
    path = "report/meetings/{meeting_id}/participants"
    key_properties = ["meeting_id", "id"]
    tap_stream_id = "report_meeting_participants"
    # data_key = "registrants"
    ignore_zoom_error_codes = []
    ignore_http_error_codes = []

    def get_records(self, single_item_str):
        """performs api querying and pagination of response."""
        path = self.path.replace("{meeting_id}", single_item_str)

        response = self.client.get(path,
                                #    params = params,
                                    endpoint = self.tap_stream_id,
                                    ignore_zoom_error_codes = self.ignore_zoom_error_codes,
                                    ignore_http_error_codes = self.ignore_http_error_codes)
        raw_records = response #.get(self.data_key, [])

        if not raw_records:
            LOGGER.warning("No records found as a response")

        yield from raw_records

    def sync(self, state, schema, stream_metadata, transformer):
        """Sync implementation for `meeting_polls` stream."""
        meeting_ids = ListMeetings(self.client).get_records()

        with metrics.record_counter(self.tap_stream_id) as counter:
            for single_item in meeting_ids :
                for record in self.get_records(str(single_item)):
                    transformed_record = transformer.transform(record, schema, stream_metadata)
                    write_record(self.tap_stream_id, transformed_record)
                    counter.increment()
        return state

STREAMS = {
    Users.tap_stream_id: Users,
    Meetings.tap_stream_id: Meetings,
    MeetingPolls.tap_stream_id: MeetingPolls,
    MeetingRegistrants.tap_stream_id: MeetingRegistrants,   #pagination
    MeetingQuestions.tap_stream_id: MeetingQuestions,
    ReportMeetings.tap_stream_id: ReportMeetings,
    ReportMeetingParticipants.tap_stream_id: ReportMeetingParticipants
}

import singer
from singer import metrics, write_record
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

STREAMS = {
    Users.tap_stream_id: Users
}
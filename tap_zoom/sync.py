import re
from datetime import datetime, timedelta, timezone

import singer
from singer import metrics, metadata, Transformer
from singer.bookmarks import set_currently_syncing

from tap_zoom.discover import discover
from tap_zoom.endpoints import ENDPOINTS_CONFIG

LOGGER = singer.get_logger()


def write_schema(stream):
    schema = stream.schema.to_dict()
    singer.write_schema(stream.tap_stream_id, schema, stream.key_properties)


def update_key_bag_for_child(key_bag, parent_endpoint, record):
    # Constructs the properties needed to build the nested
    # paths used by the Zoom APIs.
    # Ex. the list of recordings is fetched at
    #   /users/{userId}/recordings
    # We get the list of user records and pass the following
    # key bag to the recordings endpoint:
    #   {"userId": <user_id>}
    updated_key_bag = dict(key_bag)

    if parent_endpoint and 'provides' in parent_endpoint:
        for dest_key, obj_key in parent_endpoint['provides'].items():
            updated_key_bag[dest_key] = record[obj_key]

    return updated_key_bag

# This method is called for both Zoom Cloud Recordings and Zoom Phone Recordings
def sync_recordings(client,
                    catalog,
                    state,
                    required_streams,
                    selected_streams,
                    stream_name,
                    endpoint,
                    key_bag,
                    parent_endpoint=None,
                    records=[]):
    stream = catalog.get_stream(stream_name)
    write_schema(stream)

    # Also write to a table called `url_to_recordings`
    # in order to map a share_url to the meeting uuid for Zoom Cloud Recordings
    if stream_name == 'recordings':
        dependant_stream = catalog.get_stream('url_to_recordings')
        write_schema(dependant_stream)
    
    utc_format = '%Y-%m-%d'
    start_date = singer.get_bookmark(state,
                                     stream_name,
                                     'endDate',
                                     client.start_date)
    current_datetime = datetime.now(timezone.utc)
    if start_date:
        start_datetime = singer.utils.strptime_to_utc(start_date)
    else:
        # If no start_date or bookmark available, default to
        # ingesting yesterday's data.
        yesterday = current_datetime - timedelta(days=1)
        start_datetime = singer.utils.strptime_to_utc(yesterday.strftime(utc_format))

    # Continue to sync any rows during the current date in case they 
    # are still processing. The Zoom API only takes dates as parameters.
    max_date = current_datetime.strftime(utc_format)
    max_datetime = current_datetime
    if not client.sync_today:
        # Stop at midnight of the current UTC datetime in case there
        # are additional recordings/meetings in progress.    
        max_datetime = singer.utils.strptime_to_utc(max_date)

    while start_datetime < max_datetime:
        next_datetime = start_datetime + timedelta(days=1)
        end_date = next_datetime.strftime(utc_format)
        params = {
            'from': start_datetime.strftime(utc_format),
            'to': end_date
        }
        for record in records:
            # Get daily recordings for all records (users)
            # We may need to restrict this to a subset of users
            # in the future to limit the amount of data we request.
            curr_key_bag = update_key_bag_for_child(key_bag,
                                                    parent_endpoint,
                                                    record)

            # Note that the recordings endpoint can only fetch
            # up to 30 days of data at one time:
            # https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/recordingsList
            sync_endpoint(client,
                         catalog,
                         state,
                         required_streams,
                         selected_streams,
                         stream_name,
                         endpoint,
                         curr_key_bag,
                         stream_params=params,
                         should_write_schema=False)
        if next_datetime > max_datetime:
            end_date = max_date
        singer.write_bookmark(state, stream_name, 'endDate', end_date)
        start_datetime = next_datetime


def sync_child_endpoints(client,
                         catalog,
                         state,
                         required_streams,
                         selected_streams,
                         stream_name,
                         endpoint,
                         key_bag,
                         records=[]):
    if 'children' not in endpoint or len(records) == 0:
        return

    for child_stream_name, child_endpoint in endpoint['children'].items():
        if child_stream_name not in required_streams:
            continue

        update_current_stream(state, child_stream_name)
        if child_stream_name == 'recordings' or child_stream_name == 'phone_call_logs':
            # Special-handling for cloud and phone recordings bookmarks
            sync_recordings(client,
                            catalog,
                            state,
                            required_streams,
                            selected_streams,
                            child_stream_name,
                            child_endpoint,
                            key_bag,
                            parent_endpoint=endpoint,
                            records=records)
        else:
            for record in records:
                # Iterate through records and fill in relevant keys
                # for child streams.
                # Ex. 'meetings' requires a userId in the path.
                child_key_bag = update_key_bag_for_child(key_bag, endpoint, record)
                sync_endpoint(client,
                            catalog,
                            state,
                            required_streams,
                            selected_streams,
                            child_stream_name,
                            child_endpoint,
                            child_key_bag)


def sync_endpoint(client,
                  catalog,
                  state,
                  required_streams,
                  selected_streams,
                  stream_name,
                  endpoint,
                  key_bag,
                  stream_params={},
                  should_write_schema=True):
    persist = endpoint.get('persist', True)
    if persist:
        stream = catalog.get_stream(stream_name)
        schema = stream.schema.to_dict()
        mdata = metadata.to_map(stream.metadata)
        if should_write_schema:
            # Child endpoints do not need to write the schema
            # on every call to `sync_endpoints`, so we set
            # should_write_schema=False for those cases.
            write_schema(stream)

    path = endpoint['path'].format(**key_bag)

    page_size = 1000
    next_page_token = ''
    initial_load = True

    while initial_load or len(next_page_token) > 0:
        if initial_load:
            initial_load = False
        if state.get('currently_syncing') != stream_name:
            # We may have just been syncing a child stream.
            # Update the currently syncing stream if needed.
            update_current_stream(state, stream_name)

        params = {
            'page_size': page_size,
            'next_page_token': next_page_token,
            **stream_params,
        }

        data = client.get(path,
                          params=params,
                          endpoint=stream_name,
                          ignore_zoom_error_codes=endpoint.get('ignore_zoom_error_codes', []),
                          ignore_http_error_codes=endpoint.get('ignore_http_error_codes', []))

        if data is None:
            return
        
        # Skip parsing records, if an API call returns 0 'total_records'  
        if 'record_count_key' in endpoint:
            record_count = records = data[endpoint['record_count_key']]
            
            if record_count == 0:
                return
   
        if 'data_key' in endpoint:
            records = data[endpoint['data_key']]
        else:
            records = [data]

        with metrics.record_counter(stream_name) as counter:
            with Transformer() as transformer:
                for record in records:
                    
                    # Only parse phone_call_log records if a recording exists
                    # result field of the phone_call_log is 'Auto Recorded' for recorded calls
                    if 'recording_key' in endpoint:
                        result = record[endpoint['recording_key']]
                        
                        if result!='Auto Recorded':
                            continue
                    
                    if persist and stream_name in selected_streams:
                        record = {**record, **key_bag}
                        record_typed = transformer.transform(record,
                                                             schema,
                                                             mdata)
                        singer.write_record(stream_name, record_typed)
                        counter.increment()
                    
                    if stream_name == 'recordings':
                        extra_stream = 'url_to_recordings'
                        current_timestamp = datetime.now(timezone.utc)
                        url_to_recording_map = {
                            'id': record['id'],
                            'share_url': record['share_url'],
                            'uuid': record['uuid'],
                            'timestamp': singer.utils.strftime(current_timestamp)
                        }
                        singer.write_record(extra_stream, url_to_recording_map)

                sync_child_endpoints(client,
                                     catalog,
                                     state,
                                     required_streams,
                                     selected_streams,
                                     stream_name,
                                     endpoint,
                                     key_bag,
                                     records=records)

        next_page_token = data.get('next_page_token', '')
        if endpoint.get('paginate', True):
            # each endpoint has a different max page size, the server will send the one that is forced
            page_size = data['page_size']


def update_current_stream(state, stream_name=None):  
    set_currently_syncing(state, stream_name) 
    singer.write_state(state)

def get_required_streams(endpoints, selected_stream_names):
    required_streams = []
    for name, endpoint in endpoints.items():
        if endpoint.get('path') is None:
            # Skip any streams like `url_to_recordings` that don't
            # map to a specific endpoint but provide additional metadata
            # for Zoom data reports.
            continue
        child_required_streams = None
        if 'children' in endpoint:
            child_required_streams = get_required_streams(endpoint['children'],
                                                          selected_stream_names)
        if name in selected_stream_names or child_required_streams:
            required_streams.append(name)
            if child_required_streams:
                required_streams += child_required_streams

    return required_streams

def sync(client, catalog, state):
    if not catalog:
        catalog = discover()
        selected_streams = catalog.streams
    else:
        selected_streams = catalog.get_selected_streams(state)

    selected_stream_names = []
    for selected_stream in selected_streams:
        selected_stream_names.append(selected_stream.tap_stream_id)

    required_streams = get_required_streams(ENDPOINTS_CONFIG, selected_stream_names)

    for stream_name, endpoint in ENDPOINTS_CONFIG.items():
        if stream_name in required_streams:
            update_current_stream(state, stream_name)
            sync_endpoint(client,
                          catalog,
                          state,
                          required_streams,
                          selected_stream_names,
                          stream_name,
                          endpoint,
                          {})

    update_current_stream(state)

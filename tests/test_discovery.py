from tap_tester.base_suite_tests.discovery_test import DiscoveryTest
from tap_tester import menagerie
from base import ZoomBase


class ZoomDiscoveryTest(DiscoveryTest, ZoomBase):
    """Standard Discovery Test"""

    @staticmethod
    def name():
        return "tt_zoom_discovery"

    def streams_to_test(self):
        # return set(self.expected_metadata().keys())
        return self.expected_stream_names()
    
    def test_all_parent_streams_exist_in_catalog(self):
        """
        Test that all parent-tap-stream-id references point to streams 
        that actually exist in the discovered catalog.
        
        This prevents the issue where child streams reference non-existent parent streams.
        """
    
        # Get all discovered stream names
        discovered_streams = {catalog['tap_stream_id'] for catalog in self.found_catalogs}
        
        parent_streams = {}
        
        for catalog in self.found_catalogs:
            stream_name = catalog['tap_stream_id']

            schema_and_metadata = menagerie.get_annotated_schema(self.conn_id, catalog['stream_id'])
            metadata = schema_and_metadata["metadata"]
            stream_properties = [item for item in metadata if item.get("breadcrumb") == []]
            
            if stream_properties:
                stream_metadata = stream_properties[0].get("metadata", {})
                parent_id = stream_metadata.get('parent-tap-stream-id')
                if parent_id:
                    parent_streams[stream_name] = parent_id
        
        # Validate all referenced parents exist
        missing_parents = {}
        for child_stream, parent_stream in parent_streams.items():
            if parent_stream not in discovered_streams:
                if parent_stream not in missing_parents:
                    missing_parents[parent_stream] = []
                missing_parents[parent_stream].append(child_stream)
        
        # Assert no missing parents
        if missing_parents:
            error_msg = "The following parent streams are referenced but don't exist in catalog:\n"
            for missing_parent, child_streams in missing_parents.items():
                error_msg += f"'{missing_parent}' referenced by: {child_streams}\n"
            
            self.fail(error_msg)

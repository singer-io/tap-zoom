import json
import os
import tempfile
from unittest.mock import patch
import unittest
from tap_zoom.client import ZoomClient, Server5xxError


class Mockresponse:
    """ mocking response"""
    def __init__(self, params = None, status_code = 200, endpoint = '', ignore_zoom_error_codes = [], ignore_http_error_codes = []):
        self.endpoint = endpoint
        self.ignore_zoom_error_codes = ignore_zoom_error_codes
        self.ignore_http_error_codes = ignore_http_error_codes
        self.status_code = status_code
        self.params = params

def mocked_failed_500_server_error(**kwargs):
    """ mocking 500 server error response"""
    return Mockresponse(params={'page_size': 1000, 'page_number': 1}, status_code = 500, endpoint = 'list_webinars', ignore_zoom_error_codes = [200], ignore_http_error_codes = [])

class TestBackoff(unittest.TestCase):
    """ checking the backoff"""
    tmpdir = tempfile.mkdtemp()
    predictable_filename = "zoom_config.json"

    base_config = {
        "client_id": "",
        "client_secret": "",
        "refresh_token": "",
    }

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.predictable_filename = "zoom_config.json"
        return super().setUp()

    @property
    def tmp_config_path(self):
        """ creating temp config file path"""
        return os.path.join(self.tmpdir, self.predictable_filename)

         
    @patch("time.sleep")
    @patch("requests.Session.request",return_value = mocked_failed_500_server_error())
    def test_500_server_error(self, mocked_send, mocked_sleep = 1):
        """checking retries on 5xx server error"""

        with open(self.tmp_config_path, "w") as config_file:
            json.dump(self.base_config, config_file)

        client = ZoomClient(config_path=self.tmp_config_path, config=self.base_config)

        with self.assertRaises(Server5xxError):
            client.get("path")
        # checking it with call_count = 64 because self.request function is
        # getting called recursively in the code hence, for max_tries = 8, it calling it 8**2 = 64
        self.assertEqual(mocked_send.call_count, 64)

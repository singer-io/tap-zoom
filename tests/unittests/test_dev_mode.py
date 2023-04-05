import datetime
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import pytz

from tap_zoom.client import ZoomClient, strftime


class Test_ClientDevMode(unittest.TestCase):
    """Test the dev mode functionality."""

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
        return os.path.join(self.tmpdir, self.predictable_filename)

    @patch("tap_zoom.client.ZoomClient.request")
    def test_client_without_dev_mode(self, mocked_auth_post):
        """checks if the client can write refresh token and expiry to config."""

        with open(self.tmp_config_path, "w") as ff:
            json.dump(self.base_config, ff)

        mocked_auth_post.return_value =   {"refresh_token": "abcd", "access_token": "efgh", "expires_in": 3599}

        client = ZoomClient(config_path=self.tmp_config_path, dev_mode=False, config=self.base_config)
        client.refresh_access_token()
        with open(self.tmp_config_path) as config_file:
            config = json.load(config_file)
            self.assertEqual(True, "expires_in" in config)
            self.assertEqual(True, "access_token" in config)
            self.assertEqual(True, "refresh_token" in config)

    def test_devmode_accesstoken_absent(self, *args, **kwargs):
        """checks exception if access token is not present in config."""

        with open(self.tmp_config_path, "w") as config_file:
            json.dump(self.base_config, config_file)

        try:
            client = ZoomClient(config_path=self.tmp_config_path, dev_mode=True, config=self.base_config)

            client.refresh_access_token()
        except Exception as ex:
            self.assertEqual(str(ex), "Unable to locate key in config")

    @patch("tap_zoom.client.ZoomClient.request")
    def test_client_valid_token(self, mocked_auth_post):
        """checks if the client can fetch and validate refresh token and expiry
        from config."""

        config_sample = {
            "access_token": "token",
            "expires_in": strftime(datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) + datetime.timedelta(days=5)),
            **self.base_config,
        }
        with open(self.tmp_config_path, "w") as config_file:
            json.dump(config_sample, config_file)
        client = ZoomClient(config_path=self.tmp_config_path, dev_mode=True, config=config_sample)
        client.refresh_access_token()

    @patch("tap_zoom.client.ZoomClient.request")
    def test_client_invalid_token(self, mocked_auth_post):
        """checks if the client can fetch and validate refresh token and expiry from config."""
        expiry_time = strftime(datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - datetime.timedelta(minutes=5))
        config_sample = {
            "access_token": "token",
            "expires_in": expiry_time,
            **self.base_config,
        }
        with open(self.tmp_config_path, "w") as config_file:
            json.dump(config_sample, config_file)
        try:
            client = ZoomClient(config_path=self.tmp_config_path, dev_mode=True, config=config_sample)
            client.refresh_access_token()
        except Exception as ex:
            self.assertEqual(str(ex), "Access Token in config is expired, unable to authenticate in dev mode")

    def tearDown(self) -> None:
        try:
            os.remove(self.tmp_config_path)
            os.rmdir(self.tmpdir)
        except OSError:
            pass
        return super().tearDown()

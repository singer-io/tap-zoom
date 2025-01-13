import json
from datetime import timedelta

import backoff
import requests
import singer
from singer import metrics
from singer.utils import now
from .utils import write_config
from requests.exceptions import ConnectionError

LOGGER = singer.get_logger()

class Server5xxError(Exception):
    pass

class Server429Error(Exception):
    pass

def log_backoff_attempt(details):
    LOGGER.info("Error detected communicating with Zoom, triggering backoff: %d try",
                details.get("tries"))

class ZoomClient(object):
    BASE_URL = 'https://api.zoom.us/v2/'

    def __init__(self, config, config_path, dev_mode = False):
        self.__user_agent = config.get('user_agent')
        self.__session = requests.Session()
        self.__config_path = config_path
        self.config = config
        self.__access_token = None
        self.dev_mode = dev_mode
        # Setting dummy value for dev mode implementation
        self.__expires_at = now() - timedelta(seconds=10)
        self.__client_id = config.get('client_id')
        self.__client_secret = config.get('client_secret')
        self.__refresh_token = config.get('refresh_token')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__session.close()

    def refresh_access_token(self):
        if self.dev_mode:
            if self.config['access_token']:
                self.__access_token = self.config['access_token']
                return
            raise Exception("Unable to locate access token in config")

        data = self.request(
            'POST',
            url='https://zoom.us/oauth/token',
            auth=(self.__client_id, self.__client_secret),
            data={
                'refresh_token': self.__refresh_token,
                'grant_type': 'refresh_token'
            })

        self.__access_token = data['access_token']
        self.__refresh_token = data['refresh_token']
        self.__expires_at = now() + \
            timedelta(seconds=data['expires_in'] - 10) # pad by 10 seconds for clock drift

        update_config_keys = {
            'refresh_token': self.__refresh_token,
            'access_token': self.__access_token
        }
        self.config = write_config(self.__config_path, update_config_keys)

    @backoff.on_exception(backoff.expo,
                          (Server5xxError, Server429Error, ConnectionError),
                          max_tries=8,
                          on_backoff=log_backoff_attempt,
                          factor=3)

    def request(self,
                method,
                path=None,
                url=None,
                ignore_zoom_error_codes=[],
                ignore_http_error_codes=[],
                **kwargs):
        if url is None and \
            (self.__access_token is None or \
             self.__expires_at <= now()):
            self.refresh_access_token()

        if url is None and path:
            url = '{}{}'.format(self.BASE_URL, path)

        if 'endpoint' in kwargs:
            endpoint = kwargs['endpoint']
            del kwargs['endpoint']
        else:
            endpoint = None

        if 'headers' not in kwargs:
            kwargs['headers'] = {}

        kwargs['headers']['Authorization'] = 'Bearer {}'.format(self.__access_token)

        if self.__user_agent:
            kwargs['headers']['User-Agent'] = self.__user_agent

        with metrics.http_request_timer(endpoint) as timer:
            response = self.__session.request(method, url, **kwargs)
            metrics_status_code = response.status_code
            if response.status_code in [400, 404] and response.status_code < 500:
                if response.status_code in ignore_http_error_codes or \
                    (response.status_code == 400 and response.json().get('code') in ignore_zoom_error_codes):
                    metrics_status_code = 200
                return None

            timer.tags[metrics.Tag.http_status_code] = metrics_status_code

        if response.status_code >= 500:
            raise Server5xxError()

        if response.status_code == 429:
            LOGGER.warn('Rate limit hit - 429')
            raise Server429Error(response.text)

        if response.status_code == 401:
            zoom_response = response.json()
            raise Exception('Unable to authenticate because {}'.format(zoom_response['message']))

        response.raise_for_status()

        return response.json()

    def get(self, path, **kwargs):
        return self.request('GET', path=path, **kwargs)

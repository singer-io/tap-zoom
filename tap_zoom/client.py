import backoff
import requests
import singer
from singer import metrics
from requests.exceptions import ConnectionError

LOGGER = singer.get_logger()

class Server5xxError(Exception):
    pass

class RateLimitError(Exception):
    pass

class ZoomClient(object):
    BASE_URL = 'https://api.zoom.us/v2/'

    def __init__(self, config):
        self.__user_agent = config.get('user_agent')
        self.__access_token = config.get('access_token')
        self.__session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__session.close()

    ## TODO: ratelimit lib?
    @backoff.on_exception(backoff.expo,
                          (Server5xxError, RateLimitError, ConnectionError),
                          max_tries=5,
                          factor=3)
    def request(self,
                method,
                path=None,
                url=None,
                ignore_zoom_error_codes=None,
                ignore_http_error_codes=None,
                **kwargs):
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

            if response.status_code in [400, 404] and response.status_code < 500:
                if response.status_code in ignore_http_error_codes or \
                    (response.status_code == 400 and response.json().get('code') in ignore_zoom_error_codes):
                    timer.tags[metrics.Tag.http_status_code] = 200
                return None

            timer.tags[metrics.Tag.http_status_code] = response.status_code

        if response.status_code >= 500:
            raise Server5xxError()

        if response.status_code == 429:
            LOGGER.warn('Rate limit hit - 429')
            raise RateLimitError()

        response.raise_for_status()        

        return response.json()

    def get(self, path, **kwargs):
        return self.request('GET', path=path, **kwargs)

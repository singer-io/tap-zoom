#!/usr/bin/env python3

import sys
import json
import argparse

import singer
from singer import metadata

from tap_zoom.client import ZoomClient
from tap_zoom.discover import discover
from tap_zoom.sync import sync

LOGGER = singer.get_logger()

REQUIRED_CONFIG_KEYS = ['client_id', 'client_secret', 'refresh_token']

def do_discover(client):
    LOGGER.info('Testing authentication')
    try:
        client.get('users')
    except:
        raise Exception('Error could not authenticate with Zoom')

    LOGGER.info('Starting discover')
    catalog = discover()
    json.dump(catalog.to_dict(), sys.stdout, indent=2)
    LOGGER.info('Finished discover')

@singer.utils.handle_top_exception(LOGGER)
def main():
    parsed_args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)

    if parsed_args.dev:
        LOGGER.warning("Executing Tap in Dev mode")
        
    with ZoomClient(parsed_args.config, parsed_args.config_path, parsed_args.dev) as client:
        if parsed_args.discover:
            do_discover(client)
        else:
            sync(client,
                 parsed_args.catalog,
                 parsed_args.state)

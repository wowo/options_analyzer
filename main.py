from api import get_options_with_filters
from download_symbols_data import download_symbol_data
from flask import Request
from google.auth import default
from google.cloud import pubsub_v1
from notify_interesting_options import notify_interesting_options
from supabase import create_client
from utils import get_symbols_from_database
import base64
import functions_framework
import json
import logging
import os
import uuid

import sentry_sdk
from sentry_sdk.integrations.gcp import GcpIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[GcpIntegration()],
    traces_sample_rate=1.0,
    profiles_sample_rate=0.1,
)

uuid_parts = str(uuid.uuid4()).split('-')
common_unique_id = ''.join(uuid_parts[:2])


class UuidFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super(UuidFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        record.unique_id = common_unique_id
        return super(UuidFormatter, self).format(record)


handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(UuidFormatter('%(asctime)s:%(levelname)s - %(message)s - %(unique_id)s'))

logger = logging.Logger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

supabase = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_KEY')
)


def get_headers(request: Request):
    if request.method == 'OPTIONS':
        return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
        }

    return {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'text/json'
    }


@functions_framework.http
def get_options_api(request: Request):
    options = get_options_with_filters(
        supabase,
        json.loads(request.args.get('params', '[]')),
        json.loads(request.args.get('order', '[]')),
        int(request.args.get('limit', 20))
    )

    return json.dumps(options), 200, get_headers(request)


def publish_symbols_to_analyze(request: Request):
    try:
        _, project_id = default()
        logger.info(f"Publishing to project: {project_id} topic: {os.environ.get('GCP_TOPIC_ID')}")
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, os.environ.get('GCP_TOPIC_ID'))

        new_symbols = request.args.get('symbol')
        symbols = get_symbols_from_database(supabase)
        if new_symbols:
            new_symbols = new_symbols.split(',')
            symbols = symbols + new_symbols
        else:
            new_symbols = []
        logger.info(f'Starting to publishing, all: {len(symbols)} new symbols: {new_symbols}')
        for symbol in symbols:
            message_future = publisher.publish(topic_path, symbol.encode('utf-8'))
            message_future.result()
        msg = f'Published {len(symbols)} symbols, including {len(new_symbols)} new symbols'
        logger.info(msg)

        return msg, 200
    except Exception as e:
        return f"Error publishing symbols: {e}", 500


def pubsub_download_symbols_data_handler(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    logger.info(f'Received message: {pubsub_message}, resource: {context.resource}, event_id: {context.event_id}')

    download_symbol_data(pubsub_message, supabase, logger)


def send_interesting_options(request: Request):
    if request.method != 'POST':
        return f'Method {request.method} not allowed', 405

    recipient = os.environ.get('EMAIL_RECIPIENT').replace('-', ',')
    if not recipient:
        logger.error('No email recipients specified')
        return 'No email recipients specified', 500

    logger.info(f'Sending interesting stock opportunities to {recipient}')
    notify_interesting_options(supabase, recipient)
    logger.info(f'All sent')

    return '', 200

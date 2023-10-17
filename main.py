import base64

from download_symbols_data import download_symbol_data
from flask import Request
from google.cloud import pubsub_v1
from supabase import create_client
from notify_interesting_options import notify_interesting_options
from utils import get_symbols_from_database
import logging
import os

logging.basicConfig(level=logging.INFO)

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(
    os.environ.get('GCP_PROJECT_ID'),
    os.environ.get('GCP_TOPIC_ID'),
)

supabase = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_KEY')
)


def publish_symbols_to_analyze(request: Request):
    try:
        new_symbols = request.args.get('symbol')
        symbols = get_symbols_from_database(supabase)
        if new_symbols:
            new_symbols = new_symbols.split(',')
            symbols = symbols + new_symbols
        else:
            new_symbols = []
        logging.info(f'Starting to publishing, all: {len(symbols)} new symbols: {new_symbols}')
        for symbol in symbols:
            message_future = publisher.publish(topic_path, symbol.encode('utf-8'))
            message_future.result()
        msg = f'Published {len(symbols)} symbols, including {len(new_symbols)} new symbols'
        logging.info(msg)

        return msg, 200
    except Exception as e:
        return f"Error publishing symbols: {e}", 500


def pubsub_download_symbols_data_handler(event, context):

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    logging.info(f'Received message: {pubsub_message}, resource: {context.resource}, event_id: {context.event_id}')

    download_symbol_data(pubsub_message, supabase)


def send_interesting_options(request: Request):
    if request.method != 'POST':
        return f'Method {request.method} not allowed', 405

    recipient = os.environ.get('EMAIL_RECIPIENT').replace('-', ',')
    if not recipient:
        logging.error('No email recipients specified')
        return 'No email recipients specified', 500

    logging.info(f'Sending interesting stock opportunities to {recipient}')
    notify_interesting_options(supabase, recipient)
    logging.info(f'All sent')

    return '', 200

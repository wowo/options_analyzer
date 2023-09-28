import base64

from download_symbols_data import download_symbol_data
from flask import Request
from google.cloud import pubsub_v1
from supabase import create_client
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
        symbol = request.args.get('symbol')
        symbols = get_symbols_from_database(supabase)
        if symbol:
            symbols.append(symbol)
        logging.info(f'Starting to publishing, all: {len(symbols)} new symbol: {symbol}')
        for symbol in symbols:
            message_future = publisher.publish(topic_path, symbol.encode('utf-8'))
            message_future.result()
        logging.info(f'Published {len(symbols)} symbols')

        return f"Published {len(symbols)} symbols.", 200
    except Exception as e:
        return f"Error publishing symbols: {e}", 500


def pubsub_download_symbols_data_handler(event, context):

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    logging.info(f'Received message: {pubsub_message}, resource: {context.resource}, event_id: {context.event_id}')

    download_symbol_data(pubsub_message, supabase)

import os
from google.cloud import pubsub_v1
from flask import Request
from utils import get_symbols_from_database
from supabase import create_client


def publish_symbols_to_analyze(request: Request):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(
        os.environ.get('GCP_PROJECT_ID'),
        os.environ.get('GCP_TOPIC_ID'),
    )

    supabase = create_client(
        os.environ.get('SUPABASE_URL'),
        os.environ.get('SUPABASE_KEY')
    )

    try:
        symbol = request.args.get('symbol')
        symbols = get_symbols_from_database(supabase)
        if symbol:
            symbols.append(symbol)
        for symbol in symbols:
            message_future = publisher.publish(topic_path, symbol.encode('utf-8'))
            message_future.result()

        return f"Published {len(symbols)} symbols.", 200
    except Exception as e:
        return f"Error publishing symbols: {e}", 500

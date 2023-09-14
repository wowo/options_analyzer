from datetime import datetime

import requests
from supabase import create_client, Client
import os

if __name__ == '__main__':
    supabase: Client = create_client(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_KEY")
    )

    response = supabase.table('stocks')\
        .select('symbol')\
        .is_('next_earnings_date', 'null')\
        .execute()
    symbols = [x['symbol'] for x in response.data]

    for symbol in symbols:
        print(f'Fetching {symbol}')
        url = f'https://www.earningswhispers.com/api/getstocksdata/{symbol}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Content-Type': 'application/json',
            'Referer': url
        }
        response = requests.request('GET', url, headers=headers)
        if response.status_code == 200:
            data = {
                'next_earnings_date': response.json()['nextEPSDate']
            }
            supabase.table('stocks').update(data).eq('symbol', symbol).execute()

from datetime import datetime
from supabase import create_client
from utils import get_symbols_from_database
import os
import pytz
import requests

if __name__ == '__main__':
    supabase = create_client(
        os.environ.get('SUPABASE_URL'),
        os.environ.get('SUPABASE_KEY')
    )

    for symbol in get_symbols_from_database(supabase):
        print(f'Fetching {symbol} from Seeking Alpha')
        try:
            url = f'https://seekingalpha.com/api/v3/symbols/{symbol}/rating/periods?filter[periods][]=0&filter[periods][]=3&filter[periods][]=6'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
                'Content-Type': 'application/json',
                'Referer': url
            }
            response = requests.request('GET', url, headers=headers)

            data = response.json()['data'][0]
            ratings = data['attributes']['ratings']
            if response.status_code == 200:
                insert_data = {
                    'symbol': symbol,
                    'as_date': data['attributes']['asDate'],
                    'authors_count': ratings.get('authorsCount', 0),
                    'authors_rating': ratings.get('authorsRating', 0),
                    'quant_rating': ratings.get('quantRating', 0),
                    'sell_side_rating': ratings.get('sellSideRating', 0),
                    'growth_grade': ratings.get('growthGrade', 0),
                    'profitability_grade': ratings.get('profitabilityGrade', 0),
                    'momentum_grade': ratings.get('momentumGrade', 0),
                    'value_grade': ratings.get('valueGrade', 0),
                    'eps_revision_grade': ratings.get('epsRevisionGrade', 0),
                    'updated_at': datetime.now().astimezone(pytz.timezone('Poland')).isoformat()
                }
                supabase.table('ratings').upsert(insert_data).execute()
        except Exception as e:
            print(f'{symbol} exception occurred: {e}, {response.text}')

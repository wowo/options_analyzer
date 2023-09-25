from datetime import datetime
from pandas import DataFrame
from supabase import create_client, Client
from utils import get_symbols_from_database
import inflection
import json
import logging
import os
import pytz
import requests

import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
import yfinance as yf

EXPIRATION_PERIODS_COUNT = 5
STOCK_COLUMNS = ['symbol', 'industry', 'industryDisp', 'longName', 'recommendationKey', 'sector', 'sectorDisp',
                 'SandP52WeekChange', 'auditRisk', 'averageDailyVolume10Day', 'averageVolume', 'averageVolume10days',
                 'beta', 'boardRisk', 'bookValue', 'compensationRisk', 'currentPrice', 'currentRatio',
                 'dayHigh', 'dayLow', 'debtToEquity', 'dividendRate', 'dividendYield',
                 'earningsGrowth', 'earningsQuarterlyGrowth', 'ebitda', 'ebitdaMargins', 'enterpriseToEbitda',
                 'enterpriseToRevenue', 'enterpriseValue', 'fiftyDayAverage', 'fiftyTwoWeekHigh', 'fiftyTwoWeekLow',
                 'fiveYearAvgDividendYield', 'floatShares', 'forwardEps', 'forwardPE',
                 'freeCashflow', 'fullTimeEmployees', 'grossMargins', 'grossProfits', 'heldPercentInsiders',
                 'heldPercentInstitutions', 'impliedSharesOutstanding', 'lastDividendValue', 'marketCap',
                 'netIncomeToCommon', 'numberOfAnalystOpinions', 'open', 'operatingCashflow', 'operatingMargins',
                 'overallRisk', 'payoutRatio', 'pegRatio', 'previousClose', 'priceHint', 'priceToBook',
                 'priceToSalesTrailing12Months', 'profitMargins', 'quickRatio', 'recommendationMean',
                 'regularMarketDayHigh', 'regularMarketDayLow', 'regularMarketOpen', 'regularMarketPreviousClose',
                 'regularMarketVolume', 'returnOnAssets', 'returnOnEquity', 'revenueGrowth', 'revenuePerShare',
                 'shareHolderRightsRisk', 'sharesOutstanding', 'sharesPercentSharesOut', 'sharesShort',
                 'sharesShortPreviousMonthDate', 'sharesShortPriorMonth', 'shortPercentOfFloat', 'shortRatio',
                 'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 'targetMedianPrice', 'totalCash',
                 'totalCashPerShare', 'totalDebt', 'totalRevenue', 'trailingAnnualDividendRate',
                 'trailingAnnualDividendYield', 'trailingEps', 'trailingPE', 'trailingPegRatio', 'twoHundredDayAverage',
                 'volume']


def fetch_top_quant_from_seeking_alpha():
    url = 'https://seekingalpha.com/api/v3/screener_results'
    payload = json.dumps({
        'per_page': 200,
        'sort': '-quant_rating',
        'type': 'stock'
    })
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
        'Content-Type': 'application/json',
    }
    response = requests.request('POST', url, headers=headers, data=payload)
    if response.status_code != 200:
        logging.warning(f'Error {response.status_code} fetching symbols from SA: {response.text}')
        return []
    return [x['attributes']['name'] for x in response.json()['data']]


def get_symbols_for_analysis(supabase: Client):
    tickers = ['DUOL', 'ASC', 'PERI', 'ADYEY', 'JNPR', 'LUV', 'CNHI', 'AGCO', 'NU', 'CRWD', 'PYPL', 'TM',
               'SONY', 'EA', 'TTWO', 'MA', 'INTU', 'V', 'TEAM', 'HUBS', 'ADBE', 'AMD', 'GMVHF', 'BBAI', 'IMMR',
               'SMCI', 'SPLK', 'UBER', 'SPOT', 'RIVN', 'EWBC', 'PSNY', 'META', 'RBLX', 'SMWB', 'MED', 'NVDA',
               'INTC', 'FLIC', 'MMM', 'MO', 'ELBM', 'PLTR', 'CIOXY', 'BIDU', 'TCEHY', 'BABA', 'ASML', 'MNDY',
               'DOCN', 'GDDY', 'SHOP', 'MDB', 'OKTA', 'AKAM', 'FSLY', 'AFRM', 'AAPL', 'MPWR', 'SGHC',
               'NET', 'SNOW', 'DDOG', 'OTGLF', 'ABNB', 'DIS', 'NFLX', 'MSFT', 'CRM', 'AMZN', 'GOOG', 'RYAAY',
               'PATH', 'ON', 'TWLO', 'U', 'DBX', 'S']
    tickers = tickers + fetch_top_quant_from_seeking_alpha()
    tickers = tickers + get_symbols_from_database(supabase)
    return sorted(set(tickers))


def download_symbol_data(symbol: str):
    try:
        logging.info(f'Fetching symbol {symbol}')
        ticker = yf.Ticker(symbol)
        info = ticker.info
        stock_data = {inflection.underscore(k): info[k] for k in STOCK_COLUMNS if k in info}
        stock_data['updated_at'] = datetime.now().isoformat()
        supabase.table('stocks').upsert(stock_data).execute()

        expirations = ticker.options
        for expiration in expirations[:EXPIRATION_PERIODS_COUNT]:
            logging.info(f'Fetching options chain for symbol {symbol} expiration {expiration}')
            puts: DataFrame = ticker.option_chain(expiration).puts

            underscore_cols = {}
            for column in puts.columns.values:
                underscore_cols[column] = inflection.underscore(column)
            puts = puts.rename(columns=underscore_cols)
            puts.fillna(0, inplace=True)

            rows_data = []
            for index, row in puts.iterrows():
                row_data = row.to_dict()
                row_data['last_trade_date'] = row_data['last_trade_date'].isoformat()
                row_data['symbol'] = symbol
                row_data['expiration'] = expiration
                row_data['updated_at'] = datetime.now().astimezone(pytz.timezone('Poland')).isoformat()

                rows_data.append(row_data)
            try:
                supabase.table('puts').upsert(rows_data).execute()
            except Exception as e:
                print(str(e))
    except Exception as e:
        logging.error(f'Exception occurred: {e}')


if __name__ == '__main__':
    supabase = create_client(
        os.environ.get('SUPABASE_URL'),
        os.environ.get('SUPABASE_KEY')
    )

    symbols = get_symbols_for_analysis(supabase)

    for symbol in symbols:
        download_symbol_data(symbol)

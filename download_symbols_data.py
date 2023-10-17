from datetime import datetime, timedelta
from pandas import DataFrame
from supabase import create_client, Client
import inflection
import logging
import numpy as np
import os
import pytz
import scipy.stats as stats

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


def get_annualized_volatility(symbol: str) -> float:
    current_date = datetime.today().date()
    date_year_ago = current_date - timedelta(days=365)
    df = yf.download(symbol, start=date_year_ago, end=current_date)
    df['Log_Return'] = df['Close'].apply(lambda x: np.log(x)) - df['Close'].shift(1).apply(lambda x: np.log(x))
    daily_volatility = df['Log_Return'].std()
    volatility = daily_volatility * np.sqrt(252)
    return volatility


def get_black_scholes_put_delta(current_stock_price: float, strike_price: float, time_to_expire_years: float,
                                risk_free_interest_rate: float, annualized_stock_volatility: float) -> float:
    d1 = (np.log(current_stock_price / strike_price) + (risk_free_interest_rate + 0.5 * annualized_stock_volatility ** 2) * time_to_expire_years) / (annualized_stock_volatility * np.sqrt(time_to_expire_years))
    put_delta = stats.norm.cdf(d1) - 1
    return put_delta


def get_risk_free_rate_of_return() -> float:
    tnx = yf.Ticker('^IRX')
    hist = tnx.history(period='1d')
    return hist['Close'].iloc[0] / 100


def download_symbol_data(symbol: str, supabase: Client):
    try:
        logging.info(f'Fetching symbol {symbol}')
        ticker = yf.Ticker(symbol)
        info = ticker.info
        stock_data = {inflection.underscore(k): info[k] for k in STOCK_COLUMNS if k in info}
        stock_data['annualized_volatility'] = get_annualized_volatility(symbol)
        stock_data['updated_at'] = datetime.now().isoformat()
        supabase.table('stocks').upsert(stock_data).execute()

        risk_free_rate = get_risk_free_rate_of_return()

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
                days_expire = (datetime.strptime(expiration, '%Y-%m-%d').date() - datetime.today().date()).days

                row_data = row.to_dict()
                row_data['last_trade_date'] = row_data['last_trade_date'].isoformat()
                row_data['symbol'] = symbol
                row_data['expiration'] = expiration
                row_data['updated_at'] = datetime.now().astimezone(pytz.timezone('Poland')).isoformat()
                row_data['delta'] = get_black_scholes_put_delta(stock_data['current_price'], row_data['strike'],
                                                                days_expire / 365, risk_free_rate,
                                                                stock_data['annualized_volatility'])

                rows_data.append(row_data)
            try:
                supabase.table('puts').upsert(rows_data).execute()
            except Exception as e:
                print(str(e))
    except Exception as e:
        logging.error(f'Exception occurred: {e}')
        raise e


if __name__ == '__main__':
    supabase = create_client(
        os.environ.get('SUPABASE_URL'),
        os.environ.get('SUPABASE_KEY')
    )

    download_symbol_data('META', supabase)

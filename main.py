from datetime import datetime

import pytz
from pandas import DataFrame
from supabase import create_client, Client
import inflection
import os
import yfinance as yf

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

if __name__ == '__main__':
    supabase: Client = create_client(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_KEY")
    )

    ticker_names = ['DUOL', 'ASC', 'PERI', 'ADYEY', 'JNPR', 'LUV', 'CNHI', 'AGCO', 'NU', 'CRWD', 'PYPL', 'TM',
                    'SONY', 'EA', 'TTWO', 'MA', 'INTU', 'V', 'TEAM', 'HUBS', 'ADBE', 'AMD', 'GMVHF', 'BBAI', 'IMMR',
                    'SMCI', 'SPLK', 'UBER', 'SPOT', 'RIVN', 'EWBC', 'PSNY', 'META', 'RBLX', 'SMWB', 'MED', 'NVDA',
                    'INTC', 'FLIC', 'MMM', 'MO', 'ELBM', 'PLTR', 'CIOXY', 'BIDU', 'TCEHY', 'BABA', 'ASML', 'MNDY',
                    'DOCN', 'GDDY', 'SHOP', 'MDB', 'OKTA', 'AKAM', 'FSLY', 'AFRM', 'AAPL', 'MPWR', 'SGHC',
                    'NET', 'SNOW', 'DDOG', 'OTGLF', 'ABNB', 'DIS', 'NFLX', 'MSFT', 'CRM', 'AMZN', 'GOOG']

    for ticker_name in ticker_names:
        try:
            print(f'Fetching ticker {ticker_name}')
            ticker = yf.Ticker(ticker_name)
            info = ticker.info
            stock_data = {inflection.underscore(k): info[k] for k in STOCK_COLUMNS if k in info}
            stock_data['updated_at'] = datetime.now().isoformat()
            supabase.table('stocks').upsert(stock_data).execute()

            expirations = ticker.options
            for expiration in expirations[:3]:
                print(f'Fetching options chain for ticker {ticker_name} expiration {expiration}')
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
                    row_data['symbol'] = ticker_name
                    row_data['expiration'] = expiration
                    row_data['updated_at'] = datetime.now().astimezone(pytz.timezone('Poland')).isoformat()

                    rows_data.append(row_data)
                try:
                    supabase.table('puts').upsert(rows_data).execute()
                except Exception as e:
                    print(str(e))
        except Exception as e:
            print(f'Exception occurred: {e}')

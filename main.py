import inflection
import yfinance as yf
import os

from pandas import DataFrame
from supabase import create_client, Client

if __name__ == '__main__':
    supabase: Client = create_client(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_KEY")
    )

    ticker_name = 'GOOG'
    ticker = yf.Ticker(ticker_name)
    last_price = ticker.history()['Close'].iloc[-1]

    expirations = ticker.options
    for expiration in expirations[:3]:
        puts: DataFrame = ticker.option_chain(expiration).puts

        underscore_cols = {}
        for column in puts.columns.values:
            underscore_cols[column] = inflection.underscore(column)
        puts = puts.rename(columns=underscore_cols)
        puts.fillna(0, inplace=True)

        for index, row in puts.iterrows():
            row_data = row.to_dict()
            row_data['last_trade_date'] = row_data['last_trade_date'].isoformat()
            row_data['ticker'] = ticker_name
            row_data['expiration'] = expiration
            row_data['stock_last_price'] = last_price
            try:
                supabase.table('puts').upsert(row_data).execute()
            except Exception as e:
                print(row_data)
                print(str(e))


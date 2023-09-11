# options_analyzer

    select expiration, strike, ask, bid, round((stock_last_price - strike) / stock_last_price, 2) as diff, implied_volatility, open_interest, volume
    from puts
    where  (stock_last_price - strike) / stock_last_price between 0.1 and 0.2
    order by bid DESC
# options_analyzer
    
    select 
      ticker,
      expiration,
      expiration - current_date as days_until_expire,
      strike,
      bid,
      round((stock_last_price - strike) / stock_last_price, 2) as diff,
      round(implied_volatility, 4) as iv,
      open_interest,
      volume,
      last_trade_date
    from puts
    where  (stock_last_price - strike) / stock_last_price between 0.09 and 0.2
    order by bid DESC

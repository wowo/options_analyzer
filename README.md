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

# deploy http cloud function

    gcloud functions deploy publish_symbols_to_analyze --runtime python311  --trigger-http --service-account options-analyzer@quantride.iam.gserviceaccount.com --gen2 --allow-unauthenticated --region=europe-west2 --set-secrets SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_KEY:latest --env-vars-file=.env.yaml

# deploy Pub/Sub consumer

    gcloud functions deploy download_symbol_data --runtime python311  --trigger-topic symbols_to_analyze --service-account options-analyzer@quantride.iam.gserviceaccount.com --gen2 --allow-unauthenticated --region=europe-west2 --set-secrets SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_KEY:latest --env-vars-file=.env.yaml --max-instances 20
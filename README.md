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

    gcloud functions deploy publish_symbols_to_analyze --runtime python311  --trigger-http --gen2 --allow-unauthenticated --region=europe-west2 --set-secrets SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_KEY:latest,SENTRY_DSN=SENTRY_DSN:latest,GCP_TOPIC_ID=GCP_TOPIC_ID:latest --memory 512M
    gcloud functions deploy send_interesting_options --runtime python311  --trigger-http --gen2 --allow-unauthenticated --region=europe-west2 --set-secrets SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_KEY:latest,SENTRY_DSN=SENTRY_DSN:latest,EMAIL_CREDENTIALS=EMAIL_CREDENTIALS:latest,EMAIL_RECIPIENT=EMAIL_RECIPIENT:latest --memory 512M
    gcloud functions deploy get_options_api --runtime python311  --trigger-http --gen2 --allow-unauthenticated --region=europe-west2 --set-secrets SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_KEY:latest,SENTRY_DSN=SENTRY_DSN:latest --memory 512M

# deploy Pub/Sub consumer
    
     gcloud functions deploy pubsub_download_symbols_data_handler --runtime python311 --trigger-topic symbols_to_analyze --gen2 --allow-unauthenticated --region=us-central1 --set-secrets SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_KEY:latest,SENTRY_DSN=SENTRY_DSN:latest --max-instances 100 --memory 512M

# Example API call params

    ?params=[{"column": "price_strike_ratio","op": "gte","criteria": 0.1}, {"column": "current_price","op": "lte","criteria": 250},{"column": "in_the_money","op": "eq","criteria": false},{"column": "days_until_expire","op": "lte","criteria": 21},{"column": "bid_strike_ratio","op": "gte","criteria": 0.01}]&order=[{"column": "bid","dir": "desc"}]&limit=10

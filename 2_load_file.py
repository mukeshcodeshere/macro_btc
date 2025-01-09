import pandas as pd
import requests

df = pd.read_csv(r"1_coin_market_caps.csv")

print(df.head(2))
print(df.columns)

def get_btc_price():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd'
    }
    response = requests.get(url, params=params).json()
    return response['bitcoin']['usd']

# Get the current BTC price
btc_price = get_btc_price()

print(f"Latest BTC Price: {btc_price}")

# # Convert market cap to BTC equivalent
# market_caps_df['market_cap_btc'] = market_caps_df['market_cap'] / btc_price

# # Display first few rows
# market_caps_df[['id', 'symbol', 'market_cap', 'market_cap_btc']].head()

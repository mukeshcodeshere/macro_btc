import pandas as pd
import requests
import pandas_datareader.data as web
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

def get_btc_price():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd'
    }
    response = requests.get(url, params=params).json()
    return float(response['bitcoin']['usd'])

def fetch_money_supply(country_code):
    # Get today's date for the end parameter
    today = pd.to_datetime('today').strftime('%Y-%m-%d')
    
    # Example: Fetching US M2 money supply (USD) from FRED
    if country_code == 'USD':
        return web.DataReader('M2SL', 'fred', start='2000-01-01', end=today)
    else:
        raise NotImplementedError(f"Money supply data for {country_code} not implemented.")

# Get the current BTC price
btc_price = get_btc_price()

print(f"Latest BTC Price: {btc_price}")

df = pd.read_csv(r"1_coin_market_caps.csv")
print(df.columns)

# Convert market cap to BTC equivalent
df['market_cap_btc'] = df['market_cap'] / btc_price

# Aggregate the market cap in BTC
total_crypto_supply_btc = df['market_cap_btc'].sum()
print(f"Total Crypto Supply in BTC: {total_crypto_supply_btc}")
    
# Fetch US money supply data (example)
money_supply_us = fetch_money_supply('USD')

# Display the last few rows
print(money_supply_us.tail())

# Merge both data sources to create a time series for modeling
data = pd.DataFrame({
    'crypto_supply_btc': [total_crypto_supply_btc] * len(money_supply_us),
    'money_supply_us': money_supply_us['M2SL'],
    'btc_price': [btc_price] * len(money_supply_us)
}, index=money_supply_us.index)

# Check for multicollinearity
print(data.corr())

# Scale the features to ensure similar magnitudes
scaler = StandardScaler()
data[['crypto_supply_btc', 'money_supply_us']] = scaler.fit_transform(data[['crypto_supply_btc', 'money_supply_us']])

# Difference the data to remove trends
data_diff = data.diff().dropna()

# Rebuild the model with differenced data
X = data_diff[['crypto_supply_btc', 'money_supply_us']]  # Independent variables
y = data_diff['btc_price']  # Dependent variable

# Add a constant to the model (intercept)
X = sm.add_constant(X)

# Fit the model
model = sm.OLS(y, X).fit()

# Get model summary
print(model.summary())

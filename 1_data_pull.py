import requests
import pandas as pd
import time
import logging

def get_all_market_caps():
    # Setup the URL and request parameters
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',  # Convert all to USD
        'order': 'market_cap_desc',  # Order by market cap
        'per_page': 250,  # Max per page
        'page': 1,  # Start from the first page
    }
    
    # List to hold the results
    coins = []
    
    # Use a session to optimize multiple requests
    with requests.Session() as session:
        while True:
            try:
                # Make the request to the API
                response = session.get(url, params=params)
                response.raise_for_status()  # Raise an exception for bad responses (4xx/5xx)
                
                # Parse the response JSON
                data = response.json()
                
                # Break if there are no results (empty page)
                if not data:
                    logging.info(f"No more data found, stopping at page {params['page']}")
                    break
                
                # Extend our coins list with the current page's data
                coins.extend(data)
                
                # Increment the page number to get the next page
                params['page'] += 1

                # Sleep to prevent hitting rate limits
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                # Catch any exceptions and log the error, then stop
                logging.error(f"Error fetching data: {e}")
                break

            except ValueError as e:
                # In case JSON parsing fails, log and break
                logging.error(f"Error parsing response JSON: {e}")
                break
    
    # Convert to DataFrame
    df = pd.DataFrame(coins)
    
    # Optional: Drop columns that are often missing or irrelevant
    irrelevant_columns = [
        'image', 'ath', 'ath_date', 'atl', 'atl_date', 'roi', 'last_updated'
    ]
    df.drop(columns=[col for col in irrelevant_columns if col in df.columns], inplace=True)
    
    # Fill missing values or apply other data cleaning steps
    df.fillna({'market_cap': 0, 'current_price': 0, 'total_volume': 0}, inplace=True)
    
    # Return the cleaned DataFrame
    return df

# Setup logging
logging.basicConfig(level=logging.INFO)

# Fetch market cap data
market_caps_df = get_all_market_caps()

# Save DataFrame to CSV
market_caps_df.to_csv("1_coin_market_caps.csv", index=False)

# Optional: Show some sample data
logging.info(f"Sample data: \n{market_caps_df.head()}")

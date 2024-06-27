import os
import requests
import pandas as pd
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# Load environment variables from .env file
load_dotenv()

def fetch_top_cryptos(api_key, limit):
    """
    Fetches top cryptocurrencies by market capitalization from CoinMarketCap API.

    Parameters:
    - api_key (str): Your CoinMarketCap API key.
    - limit (int): Number of top cryptocurrencies to fetch (default: 10).

    Returns:
    - DataFrame: DataFrame containing the top cryptocurrencies and their market cap percentages.
    """
    # CoinMarketCap API URL
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

    parameters = {
        'start': '1',
        'limit': str(limit),  # Fetching top cryptocurrencies based on user input
        'convert': 'USD'
    }

    # Headers containing your API key
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }


    # Make a GET request to the CoinMarketCap API
    response = requests.get(url, headers=headers, params=parameters)
    
    # Check for HTTP errors
    response.raise_for_status()
    
    # Load data into pandas DataFrame
    data = response.json()
    df = pd.json_normalize(data['data'])  # Normalize JSON data into DataFrame
    
    # Selecting the 'name' and 'quote.USD.market_cap' columns
    market_cap_raw = df.loc[:, ["name", "quote.USD.market_cap"]]
    
    # Filtering out rows without a market capitalization
    cap = market_cap_raw[market_cap_raw['quote.USD.market_cap'] > 0]
    
    # Taking top cryptocurrencies based on the limit parameter
    cap = cap.head(limit)
    
    # Calculating market cap percentage
    total_market_cap = cap['quote.USD.market_cap'].sum()
    cap = cap.set_index("name")
    cap = cap.assign(market_cap_perc=lambda x: (x['quote.USD.market_cap'] / total_market_cap) * 100)
    
    return cap

def plot_top_cryptos_market_cap(dataframe, title='Top Cryptocurrencies by Market Capitalization', ylabel='% of Total Market Cap'):
    """
    Plots the market capitalization percentages of top cryptocurrencies.

    Parameters:
    - dataframe (DataFrame): DataFrame containing cryptocurrencies and their market cap percentages.
    - title (str): Title of the plot (default: 'Top Cryptocurrencies by Market Capitalization').
    - ylabel (str): Label for the y-axis (default: '% of Total Market Cap').

   
    """
    
    ax = dataframe['market_cap_perc'].plot(kind='bar', title=title, ylabel=ylabel)
    ax.set_ylabel(ylabel)
        
        # Show the plot
    plt.tight_layout()
    plt.show()
  

def main():
    # Fetch API key from environment variables
    api_key = os.getenv('COINMARKETCAP_API_KEY')
    
    # Fetch top cryptocurrencies data
    top_cryptos_data = fetch_top_cryptos(api_key, limit=10)
    
    plot_top_cryptos_market_cap(top_cryptos_data)
    
if __name__ == "__main__":
    main()

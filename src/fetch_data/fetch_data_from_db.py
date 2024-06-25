# Import necessary modules
from database_models import AssetData  # Assuming this is your model
from save_asset_and_stock import get_asset_data  # Function to fetch data from DB
import pandas as pd

# New function to fetch data from the database and convert to DataFrame
def fetch_data_from_db(asset, start_date, end_date):
  # Query the database for the asset data within the date range
  query_results = get_asset_data(asset, start_date, end_date)
  
  # Convert query results to a pandas DataFrame
  data = pd.DataFrame(list(query_results), columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
  data['Date'] = pd.to_datetime(data['Date'])
  data.set_index('Date', inplace=True)
  
  return data
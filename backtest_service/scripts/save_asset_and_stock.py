import json
from sqlalchemy.orm.exc import NoResultFound
from database_models import Dim_Assets, Dim_Date, Fact_StockPrices, init_db
import yfinance as yf
from src.shared import send_message_to_kafka, create_kafka_consumer, consume_messages, create_and_consume_messages

def load_stock_data(file_path):
  with open(file_path, 'r') as file:
    return json.load(file)

def create_or_update_assets(session, stocks):
  for stock in stocks:
    try:
      asset = session.query(Dim_Assets).filter_by(TickerSymbol=stock["ticker"]).one()
    except NoResultFound:
      asset = Dim_Assets(TickerSymbol=stock["ticker"], AssetName=stock["name"], AssetType=stock["type"])
      session.add(asset)
  session.commit()

def ensure_date_entry(session, date_key, index):
  date_entry = session.query(Dim_Date).filter_by(DateKey=date_key).first()
  if not date_entry:
    date_entry = Dim_Date(DateKey=date_key, Date=index.date(), Year=index.year, Quarter=index.quarter, Month=index.month, Day=index.day)
    session.add(date_entry)
    session.commit()

def preprocess_stock_data(hist):
  """
  Preprocess the stock data to extract and return only the OHLC values.

  Parameters:
  - hist: DataFrame containing the historical stock data.

  Returns:
  - A DataFrame with the Date as the index and columns for Open, High, Low, and Close values.
  """
  # Extracting OHLC data
  ohlc_data = hist[['Open', 'High', 'Low', 'Close']]
  return ohlc_data

def ensure_and_process_date(session, date):
  """
  Ensure the date is in the correct format and check if the date entry exists in the database.
  If not, create a new date entry.

  Parameters:
  - session: The database session.
  - date: The date to process.

  Returns:
  - The DateKey for the given date.
  """
  date_key = int(date.strftime('%Y%m%d'))
  date_entry = session.query(Dim_Date).filter_by(DateKey=date_key).first()
  if not date_entry:
    date_entry = Dim_Date(
      DateKey=date_key, 
      Date=date.date(), 
      Year=date.year, 
      Quarter=date.quarter, 
      Month=date.month, 
      Day=date.day
    )
    session.add(date_entry)
    session.commit()
  return date_key

def fetch_and_save_stock_data(session, stocks):
  for stock in stocks:
    ticker = stock["ticker"]
    stock_data = yf.Ticker(ticker)
    hist = stock_data.history(period="1mo")
    
    # Preprocess the stock data to get OHLC values
    ohlc_data = preprocess_stock_data(hist)

    asset = session.query(Dim_Assets).filter_by(TickerSymbol=ticker).one()
    asset_id = asset.AssetID

    for index, row in ohlc_data.iterrows():
      # Ensure and process the date, then get the DateKey
      date_key = ensure_and_process_date(session, index)

      existing_stock_price = session.query(Fact_StockPrices).filter_by(DateKey=date_key, AssetID=asset_id).first()
      if not existing_stock_price:
        stock_price = Fact_StockPrices(
          DateKey=date_key,
          AssetID=asset_id,
          Open=row['Open'].item(),
          High=row['High'].item(),
          Low=row['Low'].item(),
          Close=row['Close'].item()
        )
        session.add(stock_price)
    session.commit()


def create_or_update_assets_send_to_kafka(session, stocks):
  for stock in stocks:
    try:
      asset = session.query(Dim_Assets).filter_by(TickerSymbol=stock["ticker"]).one()
    except NoResultFound:
      asset = Dim_Assets(TickerSymbol=stock["ticker"], AssetName=stock["name"], AssetType=stock["type"])
      session.add(asset)
    session.commit()
    # Send asset details to Kafka after saving to DB
    asset_details = {"ticker": stock["ticker"], "name": stock["name"], "type": stock["type"]}
    send_message_to_kafka("assets", asset_details)


def consume_assets_and_fetch_data(session):
  for message in create_and_consume_messages("assets"):
    asset = [message]  # Convert message to list as fetch_and_save_stock_data expects a list
    fetch_and_save_stock_data(session, asset)


def fetch_top_20_assets():
  tickers = "AAPL MSFT GOOGL AMZN TSLA BRK-A JNJ V WMT PG JPM UNH MA INTC VZ HD PFE BAC KO"  # Example tickers
  tickers_list = tickers.split()  # Split the string into a list of ticker symbols
  top_20_assets = []
  for ticker_symbol in tickers_list:
    ticker = yf.Ticker(ticker_symbol)  # Fetch data for each ticker individually
    asset_info = ticker.info  # Now this should work, as ticker is a Ticker object with an info attribute
    # Use .get() to safely access 'shortName' and provide a default value if not found
    top_20_assets.append({
      "ticker": asset_info.get('symbol', ticker_symbol),  # Use ticker_symbol as default if 'symbol' not found
      "name": asset_info.get('shortName', asset_info.get('longName')),  # Default to 'Unknown' if 'shortName' not found
      "type": "Stock"  # Assuming all are stocks; adjust as necessary
    })
  return top_20_assets

def main():
  session = init_db()
  assets = fetch_top_20_assets()
  create_or_update_assets_send_to_kafka(session, assets)
  consume_assets_and_fetch_data(session)
  session.close()

if __name__ == "__main__":
  main()

# Modify main accordingly
def main():
  session = init_db()
  ASSETS_FILE_PATH = "backtest_service/fetch_data/assets.json"
  # assets = load_stock_data(ASSETS_FILE_PATH)
  assets = fetch_top_20_assets()
  create_or_update_assets_send_to_kafka(session, assets)
  # fetch_and_save_stock_data(session, assets)


  consume_assets_and_fetch_data(session)

  session.close()



if __name__ == "__main__":
  main()
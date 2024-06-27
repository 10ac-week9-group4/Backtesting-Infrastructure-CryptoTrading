import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_models import Base, Fact_StockPrices, Dim_Assets, Dim_Date, init_db
import yfinance as yf
from datetime import datetime

# Database Connection Setup
# DATABASE_URL = "postgresql://postgres:password@localhost:5432/trading_data"
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)
# session = Session()
session = init_db()

ASSETS_FILE_PATH = "backtest_service/fetch_data/assets.json"

# Load stock data from a JSON file
with open(ASSETS_FILE_PATH, 'r') as file:
  top_5_stocks = json.load(file)

# Create or Update Assets in the Database
for stock in top_5_stocks:
  try:
    # Check if the asset already exists
    asset = session.query(Dim_Assets).filter_by(TickerSymbol=stock["ticker"]).one()
  except NoResultFound:
    # If not, create a new asset with AssetType
    asset = Dim_Assets(TickerSymbol=stock["ticker"], AssetName=stock["name"], AssetType=stock["type"])
    session.add(asset)
session.commit()  # Commit once after adding all new assets

# Fetch and Save Stock Data
for stock in top_5_stocks:
  ticker = stock["ticker"]
  stock_data = yf.Ticker(ticker)
  hist = stock_data.history(period="1mo")
  
  # Get the AssetID
  asset = session.query(Dim_Assets).filter_by(TickerSymbol=ticker).one()
  asset_id = asset.AssetID
  
  for index, row in hist.iterrows():
    date_key = int(index.strftime('%Y%m%d'))
    # Ensure the date entry exists
    date_entry = session.query(Dim_Date).filter_by(DateKey=date_key).first()
    if not date_entry:
      date_entry = Dim_Date(DateKey=date_key, Date=index.date(), Year=index.year, Quarter=index.quarter, Month=index.month, Day=index.day)
      session.add(date_entry)
      session.commit()
  
    # Check if a stock price for this date and asset already exists
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

session.close()
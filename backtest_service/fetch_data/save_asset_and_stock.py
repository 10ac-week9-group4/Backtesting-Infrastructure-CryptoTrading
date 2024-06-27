import json
from sqlalchemy.orm.exc import NoResultFound
from database_models import Dim_Assets, Dim_Date, Fact_StockPrices, init_db
import yfinance as yf

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

def fetch_and_save_stock_data(session, stocks):
  for stock in stocks:
    ticker = stock["ticker"]
    stock_data = yf.Ticker(ticker)
    hist = stock_data.history(period="1mo")
    asset = session.query(Dim_Assets).filter_by(TickerSymbol=ticker).one()
    asset_id = asset.AssetID

    for index, row in hist.iterrows():
      date_key = int(index.strftime('%Y%m%d'))
      ensure_date_entry(session, date_key, index)

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

def main():
  session = init_db()
  ASSETS_FILE_PATH = "backtest_service/fetch_data/assets.json"
  top_5_stocks = load_stock_data(ASSETS_FILE_PATH)
  create_or_update_assets(session, top_5_stocks)
  fetch_and_save_stock_data(session, top_5_stocks)
  session.close()

if __name__ == "__main__":
  main()
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Numeric, JSON, create_engine, DateTime, func
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from .base import Base  # Assuming base.py contains the declarative base

import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:billna1@localhost:5432/trading_data")

# Function to initialize the database
def init_db():
  engine = create_engine(DATABASE_URL)
  # Base.metadata.clear()
  Base.metadata.create_all(engine)
  return scoped_session(sessionmaker(bind=engine))

# NB: init_db() must be called explicitly to initialize the database.

class Dim_Date(Base):
  __tablename__ = 'dim_date'
  DateKey = Column(Integer, primary_key=True, autoincrement=True)
  Date = Column(Date)
  Year = Column(Integer)
  Quarter = Column(Integer)
  Month = Column(Integer)
  Day = Column(Integer)
  # Relationships
  trades = relationship("Fact_Trades", backref="dim_date")
  # backtests = relationship("Fact_Backtests", backref="dim_date")
  stock_prices = relationship("Fact_StockPrices", backref="dim_date")
  crypto_prices = relationship("Fact_CryptoPrices", backref="dim_date")

class Dim_Users(Base):
  __tablename__ = 'dim_users'
  UserID = Column(Integer, primary_key=True, autoincrement=True)
  FirstName = Column(String(100))
  LastName = Column(String(100))
  UserName = Column(String(100))
  Email = Column(String(100))
  PasswordHash = Column(String(255))
  # Relationships
  trades = relationship("Fact_Trades", backref="dim_users")
  backtests = relationship("Fact_Backtests", backref="dim_users")

class Dim_Assets(Base):
  __tablename__ = 'dim_assets'
  AssetID = Column(Integer, primary_key=True, autoincrement=True)
  AssetName = Column(String(100))
  AssetType = Column(String(50))
  TickerSymbol = Column(String(10))
  # Relationships
  trades = relationship("Fact_Trades", backref="dim_assets")
  stock_prices = relationship("Fact_StockPrices", backref="dim_assets")
  crypto_prices = relationship("Fact_CryptoPrices", backref="dim_assets")

class Dim_Strategy(Base):
  __tablename__ = 'dim_strategy'
  StrategyID = Column(Integer, primary_key=True, autoincrement=True)
  StrategyIdentifier = Column(String(100))
  StrategyName = Column(String(50))
  StrategyDescription = Column(String(500))
  ParametersNames= Column(JSON)  # Modified to store specific parameter values for the strategy
   # Relationships
  trades = relationship("Fact_Trades", backref="dim_strategy")
  scenes = relationship("Dim_Scene", backref="dim_strategy")

class Dim_Scene(Base):
  __tablename__ = 'dim_scene'
  SceneID = Column(Integer, primary_key=True, autoincrement=True)
  SceneKey = Column(String(100))
  Symbol = Column(String(10))
  Cash = Column(Numeric(18, 4))
  Commission = Column(Numeric(18, 4))
  StartDate = Column(Date)
  EndDate = Column(Date)
  StrategyID = Column(Integer, ForeignKey('dim_strategy.StrategyID'))
  Parameters = Column(JSON)  # Modified to store specific parameter values for the scene
  # Relationships
  backtests = relationship("Fact_Backtests", backref="dim_scene")


class Fact_Trades(Base):
  __tablename__ = 'fact_trades'
  TradeID = Column(Integer, primary_key=True, autoincrement=True)
  DateKey = Column(Integer, ForeignKey('dim_date.DateKey'))
  UserID = Column(Integer, ForeignKey('dim_users.UserID'))
  AssetID = Column(Integer, ForeignKey('dim_assets.AssetID'))
  StrategyID = Column(Integer, ForeignKey('dim_strategy.StrategyID'))
  TradeType = Column(String(10))
  Quantity = Column(Numeric(18, 4))
  PricePerUnit = Column(Numeric(18, 4))

class Fact_Backtests(Base):
  __tablename__ = 'fact_backtests'
  BacktestID = Column(Integer, primary_key=True, autoincrement=True)
  CreatedAt = Column(DateTime, default=func.now())  # Add this line to store the current timestamp
  UserID = Column(Integer, ForeignKey('dim_users.UserID'))
  SceneID = Column(Integer, ForeignKey('dim_scene.SceneID'))
  MaxDrawdown = Column(Numeric(18, 4))
  SharpeRatio = Column(Numeric(18, 4))
  Return = Column(Numeric(18, 4))
  TradeCount = Column(Integer)
  WinningTrades = Column(Integer)
  LosingTrades = Column(Integer)
  StartPortfolio = Column(Numeric(18, 4))
  FinalPortfolio = Column(Numeric(18, 4))

class Fact_StockPrices(Base):
  __tablename__ = 'fact_stock_prices'
  StockPriceID = Column(Integer, primary_key=True, autoincrement=True)
  DateKey = Column(Integer, ForeignKey('dim_date.DateKey'))
  AssetID = Column(Integer, ForeignKey('dim_assets.AssetID'))
  Open = Column(Numeric(18, 4))
  High = Column(Numeric(18, 4))
  Low = Column(Numeric(18, 4))
  Close = Column(Numeric(18, 4))

class Fact_CryptoPrices(Base):
  __tablename__ = 'fact_crypto_prices'
  CryptoPriceID = Column(Integer, primary_key=True, autoincrement=True)
  DateKey = Column(Integer, ForeignKey('dim_date.DateKey'))
  AssetID = Column(Integer, ForeignKey('dim_assets.AssetID'))
  Open = Column(Numeric(18, 4))
  High = Column(Numeric(18, 4))
  Low = Column(Numeric(18, 4))
  Close = Column(Numeric(18, 4))
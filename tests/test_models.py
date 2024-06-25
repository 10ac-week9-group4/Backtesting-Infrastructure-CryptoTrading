import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database_models import Base, Dim_Users, Dim_Assets


@pytest.fixture(scope='module')
def db_engine():
  return create_engine('sqlite:///:memory:')  # Use in-memory SQLite database for tests

@pytest.fixture(scope='module')
def db_session(db_engine):
  Base.metadata.create_all(db_engine)  # Create tables
  Session = scoped_session(sessionmaker(bind=db_engine))
  yield Session()
  Session.remove()
  Base.metadata.drop_all(db_engine)  # Drop tables after tests


def test_user_creation(db_session):
  # Insert a new user
  new_user = Dim_Users(UserName='testuser', Email='test@example.com', PasswordHash='hash')
  db_session.add(new_user)
  db_session.commit()

  # Query the inserted user
  user = db_session.query(Dim_Users).filter_by(UserName='testuser').first()
  assert user is not None
  assert user.Email == 'test@example.com'

def test_asset_creation(db_session):
    new_asset = Dim_Assets(AssetName='Bitcoin', AssetType='Cryptocurrency', TickerSymbol='BTC')
    db_session.add(new_asset)
    db_session.commit()

    asset = db_session.query(Dim_Assets).filter_by(TickerSymbol='BTC').first()
    assert asset is not None
    assert asset.AssetName == 'Bitcoin'


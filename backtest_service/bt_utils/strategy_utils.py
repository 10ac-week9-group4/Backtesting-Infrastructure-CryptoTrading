import hashlib
import json
from database_models import Dim_Strategy, init_db
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

"""
  :param strategy_params: A dictionary containing the strategy parameters.
      e.g  {
            "name": "SMACrossOver",
            "parameters": {
              "short_window": 20,
              "long_window": 50,
              "interval": "1d"
            },
            "description": "This strategy uses a simple moving average crossover to ..."
          }
  :param session: The database session object.
"""

def get_strategy_by_identifier(strategy_params, session=None):
  """
  Get a strategy by identifier.

  :param strategy_params: A dictionary containing the strategy parameters.

  :param session: The database session object.
  :return: The strategy object if it exists, None otherwise.
  """
  # Serialize strategy parameters to create a unique identifier
  serialized_params = json.dumps(strategy_params, sort_keys=True)
  strategy_identifier = hashlib.sha256(serialized_params.encode()).hexdigest()

  # Check if a strategy with this identifier already exists
  existing_strategy = session.query(Dim_Strategy).filter_by(StrategyIdentifier=strategy_identifier).first()
  return existing_strategy

def get_strategy_by_name(strategy_name, session=None):
    """
    Get a strategy by name.

    :param strategy_name: The name of the strategy.
    :param session: The database session object.
    
    :return: The strategy object if it exists, None otherwise.
    """
    if session is None:
        session = init_db()
    # Query for a strategy by name
    try:
        return session.query(Dim_Strategy).filter_by(StrategyName=strategy_name).first()
    except SQLAlchemyError as e:
        print(f"Failed to fetch strategy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the strategy."
        ) from e

def save_strategy(strategy_params, session=None):
  """
  Save a new strategy to the database.
    - If a strategy with the same parameters already exists, return the existing StrategyID.
    - If the strategy does not exist, create and save the new strategy.

  :param strategy_params: A dictionary containing the strategy parameters.
      e.g  {
            "name": "SMACrossOver",
            "parameters": {
              "short_window": 20,
              "long_window": 50,
              "interval": "1d"
            },
            "description": "This strategy uses a simple moving average crossover to ..."
          },
  :param session: The database session object.
  :return: The StrategyID of the newly saved strategy or the existing strategy.

  """
  if session is None:
    session = init_db()

  existing_strategy = get_strategy_by_identifier(strategy_params, session)

  parameter_names = json.dumps([key for key in strategy_params['parameters'].keys() if key != 'interval'])

  if existing_strategy is None:
    # If it does not exist, create and save the new strategy
    strategy = Dim_Strategy(
      StrategyIdentifier=hashlib.sha256(json.dumps(strategy_params, sort_keys=True).encode()).hexdigest(),
      StrategyName=strategy_params['name'],
      StrategyDescription=strategy_params["description"],
      ParametersNames=parameter_names
    )
    session.add(strategy)
    session.commit()
    return strategy.StrategyID  # Return the new StrategyID
  else:
    # If it exists, return the existing StrategyID
    return existing_strategy.StrategyID
  
import hashlib
import json
from database_models import Dim_Strategy

def get_strategy_by_identifier(strategy_params, session):
  """
  Get a strategy by identifier.

  :param strategy_params: A dictionary containing the strategy parameters.
      e.g. {
            "indicator": "SMACrossOver",
            "indicator_params": {
              "fast_period": 15,
              "slow_period": 200
            }
  :param session: The database session object.
  :return: The strategy object if it exists, None otherwise.
  """
  # Serialize strategy parameters to create a unique identifier
  serialized_params = json.dumps(strategy_params, sort_keys=True)
  strategy_identifier = hashlib.sha256(serialized_params.encode()).hexdigest()

  # Check if a strategy with this identifier already exists
  existing_strategy = session.query(Dim_Strategy).filter_by(StrategyIdentifier=strategy_identifier).first()
  return existing_strategy

def get_strategy_by_name(strategy_name, session):
    """
    Get a strategy by name.

    :param strategy_name: The name of the strategy.
    :param session: The database session object.
    :return: The strategy object if it exists, None otherwise.
    """
    # Query for a strategy by name
    existing_strategy = session.query(Dim_Strategy).filter_by(StrategyName=strategy_name).first()
    return existing_strategy

def save_strategy(strategy_params, session):
  """
  Save a new strategy to the database.

  If a strategy with the same parameters already exists, return the existing StrategyID.

  :param strategy_params: A dictionary containing the strategy parameters.
     e.g. {
            "indicator": "SMACrossOver",
            "indicator_params": {
              "fast_period": 15,
              "slow_period": 200
            }
          }
  :param session: The database session object.
  :return: The StrategyID of the newly saved strategy or the existing strategy.

  """

  existing_strategy = get_strategy_by_identifier(strategy_params, session)

  if existing_strategy is None:
    # If it does not exist, create and save the new strategy
    strategy = Dim_Strategy(
      StrategyIdentifier=hashlib.sha256(json.dumps(strategy_params, sort_keys=True).encode()).hexdigest(),
      StrategyName=strategy_params['indicator'],
      StrategyDescription=json.dumps(strategy_params),
      Indicator=strategy_params['indicator'],
      IndicatorParameterNames=json.dumps(list(strategy_params['indicator_params'].keys()))
    )
    session.add(strategy)
    session.commit()
    return strategy.StrategyID  # Return the new StrategyID
  else:
    # If it exists, return the existing StrategyID
    return existing_strategy.StrategyID
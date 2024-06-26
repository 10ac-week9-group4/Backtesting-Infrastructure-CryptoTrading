import hashlib
import json
from database_models import Dim_Strategy

def get_strategy_by_identifier(strategy_params, session):
  # Serialize strategy parameters to create a unique identifier
  serialized_params = json.dumps(strategy_params, sort_keys=True)
  strategy_identifier = hashlib.sha256(serialized_params.encode()).hexdigest()

  # Check if a strategy with this identifier already exists
  existing_strategy = session.query(Dim_Strategy).filter_by(StrategyIdentifier=strategy_identifier).first()
  return existing_strategy

def get_strategy_by_name(strategy_name, session):
    # Query for a strategy by name
    existing_strategy = session.query(Dim_Strategy).filter_by(StrategyName=strategy_name).first()
    return existing_strategy

def save_strategy(strategy_params, session):
  existing_strategy = get_strategy_by_identifier(strategy_params, session)

  if existing_strategy is None:
    # If it does not exist, create and save the new strategy
    strategy = Dim_Strategy(
      StrategyIdentifier=hashlib.sha256(json.dumps(strategy_params, sort_keys=True).encode()).hexdigest(),
      StrategyName=strategy_params['indicator'],
      StrategyDescription=json.dumps(strategy_params),
      Indicator=strategy_params['indicator'],
      IndicatorParameterNames=json.dumps(list(strategy_params['indicator_params_range'].keys()))
    )
    session.add(strategy)
    session.commit()
    return strategy.StrategyID  # Return the new StrategyID
  else:
    # If it exists, return the existing StrategyID
    return existing_strategy.StrategyID
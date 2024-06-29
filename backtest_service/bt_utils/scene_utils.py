import hashlib
import json
from database_models import Dim_Scene

def generate_scene_key(scene):
  """
  Generate a unique scene key based on the scene parameters.

  :param scene: A dictionary containing the scene parameters.
      e.g. {
              "asset": "AAPL",
              "cash": 100000,
              "commission": 0.005,
              "start_date": "2020-01-01",
              "end_date": "2021-01-01",
              "strategy": "SMACrossOver",
              "parameters": {
                  "fast_period": 15,
                  "slow_period": 200
              }
            }
          
            
  :return: A unique scene key (hashed string) e.g "a1b2c3d4e5f6g7h8i9j0"
  """
  serialized_params = json.dumps(scene, sort_keys=True)
  return hashlib.sha256(serialized_params.encode()).hexdigest()

def get_scene_by_key(session, scene):
  print("Getting scene by key...")
  scene_key = generate_scene_key(scene)
  print("Scene key: ", scene_key)
  return session.query(Dim_Scene).filter_by(SceneKey=scene_key).first()

def save_scene(scene, strategy_id, session):
  scene_key = generate_scene_key(scene)
  existing_scene = get_scene_by_key(session, scene)
  print("Existing scene: ", existing_scene)

  if existing_scene is None:
    new_scene = Dim_Scene(
      SceneKey=scene_key,
      StrategyID=strategy_id,
      Symbol=scene["asset"],
      Cash=scene["cash"],
      Commission=scene["commission"],
      StartDate=scene["start_date"],
      EndDate=scene["end_date"],
      Parameters=json.dumps(scene["parameters"])
    )
    session.add(new_scene)
    session.commit()
    return new_scene
  else:
    return existing_scene

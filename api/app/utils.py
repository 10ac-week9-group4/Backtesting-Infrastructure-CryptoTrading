from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import hashlib
import json


import os
# import sys
# sys.path.append(os.path.abspath(os.path.join('../', 'app')))
from database_models.models import Dim_Users, Dim_Assets, init_db  # Adjust the import path as necessary

# Dependency to get DB session
def get_db():
  db = init_db()
  try:
    yield db
  finally:
    db.close()

# Get the user by username from the database
def get_user_by_username(username: str):
  db_gen = get_db()
  db = next(db_gen)
  try:
    return db.query(Dim_Users).filter(Dim_Users.UserName == username).first()
  finally:
    # Manually close the db to ensure cleanup
    next(db_gen, None)

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

# get all the assets in the database
def fetch_all_assets_from_db():
  db_gen = get_db()
  db = next(db_gen)
  try:
    return db.query(Dim_Assets).all()
  finally:
    # Manually close the db to ensure cleanup
    next(db_gen, None)

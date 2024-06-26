from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import os
# import sys
# sys.path.append(os.path.abspath(os.path.join('../', 'app')))
from database_models.models import Dim_Users, init_db  # Adjust the import path as necessary

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
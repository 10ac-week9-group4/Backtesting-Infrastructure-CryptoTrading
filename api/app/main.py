import os
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import logging
import json
import os
import coloredlogs
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app import get_db


os.chdir("../")

from shared import create_and_consume_messages
from shared import send_message_to_kafka

# topic_name = "backtest_results_testing"

USER_REGISRATION_TOPIC = "user_registration"
USER_LOGIN_TOPIC = "user_login"

app = FastAPI()

# Set up logging
coloredlogs.install()  # install a handler on the root logger

logger = logging.getLogger(__name__)
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Environment variables and constants for authentication
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "secret")  
ALGORITHM = os.getenv("ALGORITHM", "HS256")  
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# Main FastAPI application
app = FastAPI()

# Pydantic models for data validation
class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="johndoe")
    email: str = Field(..., example="johndoe@example.com")
    password: str = Field(..., min_length=8)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    # Get the current time in UTC using datetime.now(datetime.timezone.utc)
    expire = datetime.now(timezone.utc) + expires_delta 
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # In a real application, we fetch user data from your database
    # For this example, we'll just hardcode a user

    # **Important:**  Replace this with actual user retrieval logic
    # user = None  # Fetch user from your database based on form_data.username
    print("FORM DATA: ", form_data.password)
    # Query the database for the user
    user = db.query(Dim_Users).filter(Dim_Users.UserName == form_data.username).first()
    logger.info("User: ", user)

    # user = {
    #     "username": "doen",
    #     "email": "doentest@gmail.com",
    #     "hashed_password": "$2b$12$8dUj8h2tzXLvej8kHwYZrejTHLv6Zq5rKv34Nijo8cHGb7WLimiEm"
    # }

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    hashed_password = user.get("hashed_password")

    # Verify password
    if not pwd_context.verify(form_data.password, hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Create and return JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.get("username")}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "username": user.get("username")}


@app.post("/register")
async def register(user: User):
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    # Create a new user dictionary
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password  # Store the hashed password
    }

    try:
        # Send registration data to Kafka
        is_success = send_message_to_kafka("user_registrations", user_data)
        if is_success:
            return {"message": "User registered successfully", "success": True, "data": user_data, "statusCode": 200 }
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send message to Kafka.")
    except Exception as e:
        logger.error(f"Error sending message to Kafka: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
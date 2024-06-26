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
from utils import get_user_by_username

from pydantic import BaseModel, Field
from datetime import date
from typing import Dict, Any
from decimal import Decimal

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
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # Query the database for the user
        user = get_user_by_username(form_data.username)
        username = user.UserName
        # logger.info("User: %s", user.UserName)
        
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        # Ensure user data contains 'hashed_password'
        hashed_password = user.PasswordHash
        if not hashed_password:
            logger.error("User data does not contain 'hashed_password'")
            raise HTTPException(status_code=500, detail="Internal server error")

        # Verify password
        if not pwd_context.verify(form_data.password, hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        # Create and return JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, 
                "token_type": "bearer", 
                "username": username, 
                "statusCode": 200, 
                "success": True, 
                "message": "User logged in successfully"
            }
    
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions (these are expected errors like incorrect username/password)
        raise http_ex
    except Exception as ex:
        logger.error(f"Unexpected error during login: {ex}")
        # Return a generic error message
        raise HTTPException(status_code=500, detail="Internal server error")

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
    


# Step 1: Define the Data Model

from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Dict, Any
from decimal import Decimal

class Parameters(BaseModel):
    start_date: date = Field(..., example="2022-12-19")
    end_date: date = Field(..., example="2023-02-19")
    cash: Decimal = Field(gt=Decimal('0'), example=Decimal('100000'))
    commission: Decimal = Field(gt=Decimal('0'), lt=Decimal('1'), example=Decimal('0.001'))
    indicator: str = Field(..., example="SmaCrossOver")
    indicator_params: Dict[str, Any] = Field(..., example={"pfast": 10, "pslow": 30})

    def to_json_serializable_dict(self):
        # Use a dictionary comprehension to convert all Decimal values to strings
        serializable_dict = {k: (str(v) if isinstance(v, Decimal) else v) for k, v in self.dict().items()}
        # Convert date fields to isoformat
        serializable_dict["start_date"] = self.start_date.isoformat()
        serializable_dict["end_date"] = self.end_date.isoformat()
        return serializable_dict

# Step 2: Create the Endpoint
@app.post("/backtest_scene")
async def backtest(parameters: Parameters):
    try:
        parameters_json_serializable = parameters.to_json_serializable_dict()
        is_success = send_message_to_kafka("scenes_topic", parameters_json_serializable)
        if is_success:
            return {"message": "Data sent to Kafka successfully", "success": True}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send message to Kafka.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error sending message to Kafka: {e}")
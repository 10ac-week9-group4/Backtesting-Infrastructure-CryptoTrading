import os
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
import websockets
from pydantic import BaseModel, Field
from datetime import date
from typing import Dict, Any
from decimal import Decimal
from shared import create_and_consume_messages, create_kafka_consumer, consume_messages
from shared import send_message_to_kafka

os.chdir("../")
from api.utils import get_user_by_username, fetch_all_assets_from_db, generate_scene_key


# topic_name = "backtest_results_testing"

USER_REGISRATION_TOPIC = "user_registration"
USER_LOGIN_TOPIC = "user_login"

app = FastAPI()

# Define a list of allowed origins for CORS
origins = [
    "http://localhost:3000",  # Add other origins as needed
]

# Add CORSMiddleware to the application instance
app.add_middleware(
    CORSMiddleware,
    # allow_origins="origins",  # Allows specified origins
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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
    first_name: str = Field(..., min_length=1, max_length=50, example="John")
    last_name: str = Field(..., min_length=1, max_length=50, example="Doe")
    username: str = Field(..., min_length=3, max_length=50, example="johndoe")
    email: str = Field(..., example="johndoe@example.com")
    password: str = Field(
        ...,
        min_length=8,
        error_messages={
            "min_length": "Password must be at least 8 characters long",
        },
    )

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
        print(form_data.username)
        # Query the database for the user
        user = get_user_by_username(form_data.username)
        print("USER", user)
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

        username = user.UserName
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
        "first_name": user.first_name,
        "last_name": user.last_name,
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
    symbol: str = Field(..., example="AAPL")
    start_date: date = Field(..., example="2022-12-19")
    end_date: date = Field(..., example="2023-02-19")
    cash: Decimal = Field(gt=Decimal('0'), example=Decimal('100000'))
    commission: Decimal = Field(gt=Decimal('0'), lt=Decimal('5'), example=Decimal('0.001'))
    strategy: str = Field(..., example="SmaCrossOver")
    parameters: Dict[str, Any] = Field(..., example={"pfast": 10, "pslow": 30})

    def to_json_serializable_dict(self):
        # Use a dictionary comprehension to convert all Decimal values to strings
        serializable_dict = {k: (str(v) if isinstance(v, Decimal) else v) for k, v in self.dict().items()}
        # Convert date fields to isoformat
        serializable_dict["start_date"] = self.start_date.isoformat()
        print("SERIALIZABLE DICT", serializable_dict)
        serializable_dict["end_date"] = self.end_date.isoformat()
        return serializable_dict


@app.post("/backtest_scene")
async def backtest(parameters: Parameters):
    try:
        parameters_json_serializable = parameters.to_json_serializable_dict()
        print("GOT HERE")
        scene_key = generate_scene_key(parameters_json_serializable)
        # add scene_key to parameters
        parameters_json_serializable["scene_key"] = scene_key
        print("SCENE KEY IN API", scene_key)
        is_success = send_message_to_kafka("scenes_topic", parameters_json_serializable)

        if is_success:
            return {"message": "Data sent to Kafka successfully", "success": True, "scene_key": scene_key}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send message to Kafka.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error sending message to Kafka: {e}")

# endpoint to fetch assets from db
@app.get("/assets")
async def get_assets():
    try:
        assets = fetch_all_assets_from_db()
        return {"assets": assets}
    except Exception as e:
        logger.error(f"Error sending message to Kafka: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
from confluent_kafka import Consumer, KafkaError

results_storage = {}

def consume_messages(topic, group_id, target_id):
    c = Consumer({
        'bootstrap.servers': 'kafka:9092',
        'group.id': group_id,
        'auto.offset.reset': 'earliest'
    })

    c.subscribe([topic])

    try:
        while True:
            msg = c.poll(1.0)  # Adjust poll timeout as needed

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            try:
                # Attempt to decode and parse the message data as JSON
                message_data = json.loads(msg.value().decode('utf-8'))
                # message_data = dict(message_data)
                print("MESSAGE DATA", message_data)
                
                # Check if message_data is indeed a dictionary
                print("Type of message_data:", type(message_data))
                if not isinstance(message_data, dict):
                    raise ValueError("message_data is not a dictionary")
                if message_data.get('scene_key') == target_id:
                    print(f"Found message for ID {target_id}: {message_data}")
                    results_storage[target_id] = message_data
                    print("RESULTS STORAGE IN CONSUMER", results_storage)
                    # yield message_data
                    # Process or store the message as needed
                    break  # or continue, depending on your use case
            except json.JSONDecodeError as e:
                # Handle cases where the message is not valid JSON
                print(f"Error decoding message to JSON: {e}")
                # Decide how to handle non-JSON messages, e.g., skip, log, etc.
                continue
            except ValueError as e:
                # Handle the case where message_data is not a dictionary
                print(e)
                continue

    finally:
        c.close()

# Example usage
# consume_messages('your_topic', 'your_group_id', 'specific_id_you_are_looking_for')
from fastapi import BackgroundTasks
# endpoint to fetch backtest results
@app.get("/backtest_results/{scene_id}")
async def get_backtest_results(scene_id: str, background_tasks: BackgroundTasks):
    # Get the scene_id from the path parameter
    print("SCENE KEY IN BACKTEST RESULTS", scene_id)

    try:
        # backtest_results = consume_messages("bt_results", "bt_results_group", scene_id)
        # return {"backtest_results": backtest_results}
        # Clear previous results to avoid mixing data
        results_storage[scene_id] = None


        # Add the consume_messages function to background tasks
        background_tasks.add_task(consume_messages, "bt_results", "bt_results_group", scene_id)

        # Inform the client that the task is started
        return {"message": "Backtest results processing started"}
    except Exception as e:
        logger.error(f"Error sending message to Kafka: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@app.get("/get_results/{scene_id}")
async def get_results(scene_id: str):
    print("SCENE KEY IN GET RESULTS", scene_id)
    print("RESULTS STORAGE", results_storage)

    if scene_id in results_storage:
        if results_storage[scene_id] is None:
            return {"message": "Results are still processing", "processing": True}
        return {"backtest_results": results_storage[scene_id], "processing": False, "message": "Results are ready!"}
    else:
        return {"error": "No such task or results expired"}
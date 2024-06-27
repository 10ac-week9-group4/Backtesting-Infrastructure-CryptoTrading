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

os.chdir("../")
from api.utils import get_user_by_username

from shared import create_and_consume_messages, create_kafka_consumer, consume_messages
from shared import send_message_to_kafka

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
    commission: Decimal = Field(gt=Decimal('0'), lt=Decimal('1'), example=Decimal('0.001'))
    strategy: str = Field(..., example="SmaCrossOver")
    parameters: Dict[str, Any] = Field(..., example={"pfast": 10, "pslow": 30})

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
    



from fastapi import FastAPI, WebSocket, HTTPException, status
from fastapi.responses import StreamingResponse
from confluent_kafka import Consumer, KafkaError, TopicPartition
import json
import asyncio

# ... other imports ...
async def generate_results(consumer):
    """Asynchronous generator function to yield backtest results from Kafka."""
    try:
        while True:
            msg = consumer.poll(5.0)  # Poll with a timeout
            logger.info("MSG", msg)
            if msg is None:
                print("No message available within timeout")
                await asyncio.sleep(0.1)  # Yield to other tasks
                continue

            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue

            print(f"Received message: {msg.value()}")
            result = json.loads(msg.value().decode('utf-8'))
            if result.get("scene_id") == scene_id:
                yield f"data: {json.dumps(result)}\n\n"
                break  # Exit loop after finding the result
    finally:
        consumer.close()

def create_kafka_consumer(topic_name, kafka_bootstrap_servers="kafka:9092", group_id_suffix='consumer'):
  group_id = f"{topic_name}_{group_id_suffix}"
  conf = {
    'bootstrap.servers': kafka_bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest'
  }
  consumer = Consumer(conf)
  consumer.subscribe([topic_name])
  return consumer

async def consume_messages_1(consumer):
  while True:
    msg = consumer.poll(1.0)
    if msg is None:
      await asyncio.sleep(1)  # Sleep if no message is available
      continue
    if msg.error():
      if msg.error().code() == KafkaError._PARTITION_EOF:
        continue
      else:
        print(f"Error while consuming message: {msg.error()}")
        continue
    yield json.loads(msg.value().decode('utf-8'))



@app.websocket("/ws/backtest_results")
async def websocket_backtest_results(websocket: WebSocket, scene_id: str):
    """WebSocket endpoint to receive backtest results for a specific scene ID."""
    await websocket.accept()
    try:
        for message in consume_from_kafka("backtest_results"):
            if message.get("scene_id") == scene_id:
                await websocket.send_text(json.dumps(message))
                break  # Stop consuming after finding the result
    except websockets.WebSocketException as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

from starlette.websockets import WebSocketState
from typing import Optional

from fastapi import Cookie, Depends, FastAPI, Query, WebSocket, status
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketState

async def get_cookie_or_token(
    session = Cookie(None),
    token = Query(None),
    ):
    if session is None and not token:
        return None

    return session or token

@app.websocket("/ws/scenes")
async def websocket_endpoint(
    websocket: WebSocket,
    # item_id: str,
    # q: Optional[int] = None,
    cookie_or_token: str = Depends(get_cookie_or_token),
):
    await websocket.accept()

    if not cookie_or_token:
        return await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    while True:
        data = await websocket.receive_text()
        await websocket.send_text(
            f"Session cookie or query token value is: {cookie_or_token}"
        )
        if q is not None:
            await websocket.send_text(f"Query parameter q is: {q}")
        await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")

# async def websocket_backtest_results(websocket: WebSocket):
#     """WebSocket endpoint to receive backtest results from Kafka consumer and stream to frontend."""
#     await websocket.accept()
#     print("IN WEB SOCKET")
#     try:
#         async for message in websocket.iter_text():
#             # Process the message (e.g., store in a cache, send to connected clients)
#             logger.info(f"Received backtest result: {message}")
#             # Assuming you have a function to broadcast to connected clients

#             # if websocket.client_state != WebSocketState.DISCONNECTED:

#             attempt = 0
#             max_retries = 5
#             retry_delay = 2
#             while attempt < max_retries:
#                 try:
#                     message_json = json.dumps(message)

#                     await websocket.send_text(message_json)  # Use send_text method

#                     # return  # Exit function after successful sending
#                 except Exception as e:
#                     print(f"Attempt {attempt + 1}: Failed to forward message, Error: {e}")
#                     attempt += 1  
#                     await asyncio.sleep(retry_delay)  # Wait before retrying

#     except websockets.WebSocketException as e:
#         logger.error(f"WebSocket error: {e}")
#     finally:
#         # Check if the WebSocket connection is still open before attempting to close
#         if websocket.client_state != WebSocketState.DISCONNECTED:
#             await websocket.close()


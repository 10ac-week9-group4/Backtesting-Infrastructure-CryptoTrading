# Import necessary modules and functions
from fastapi import FastAPI, WebSocket
import json
import logging
import coloredlogs
from starlette.websockets import WebSocketState
from sqlalchemy.orm import Session
from database_models import Dim_Users, init_db

# Initialize FastAPI app
app = FastAPI()

# Set up colored logs
coloredlogs.install()

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", format="%(levelname)s - %(message)s")

# Log service start
logger.info("Database Service started")

# Initialize the database using models.py's init_db function
db_session = init_db()

def add_user_to_database(user_data: dict, db: Session):
    """
    Add a new user to the database.
    """
    # Create a new user instance
    new_user = Dim_Users(UserName=user_data['username'], Email=user_data['email'], PasswordHash=user_data['hashed_password'])
    # Add the new user to the session and commit
    db.add(new_user)
    db.commit()
    # Refresh to get the new user instance from the database
    db.refresh(new_user)
    return new_user

@app.websocket("/ws/user_registrations")
async def websocket_user_registrations(websocket: WebSocket):
    await websocket.accept()
    try:
        async for message_str in websocket.iter_text():
            # Parse the incoming message
            message = json.loads(message_str)
            logger.info(f"Received user registration data: {message}")
            try:
                # Use the initialized DB session
                db = db_session()
                # Insert user registration data into the database
                add_user_to_database(message, db)
                # Close the session
                db.close()
            except Exception as e:
                logger.error(f"Error processing user registration: {e}")
    finally:
        if not websocket.client_state == WebSocketState.DISCONNECTED:
            await websocket.close()
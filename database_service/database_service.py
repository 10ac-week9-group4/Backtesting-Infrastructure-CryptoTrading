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
    Add a new user to the database if they do not already exist.
    """
    # Check if the user already exists in the database
    existing_user = db.query(Dim_Users).filter(Dim_Users.Email == user_data['email']).first()
    print("EXISTING USER: ", existing_user)
    if existing_user:
        # User already exists, handle accordingly (e.g., return existing user or raise an exception)
        return existing_user  # or raise Exception("User already exists.")
    
    # If the user does not exist, proceed to create a new user instance
    new_user = Dim_Users(
        FirstName=user_data['first_name'],
        LastName=user_data['last_name'],
        UserName=user_data['username'], 
        Email=user_data['email'], 
        PasswordHash=user_data['hashed_password']
    )
    
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

@app.websocket("/ws/scenes")
async def websocket_scene_handling(websocket: WebSocket):
    await websocket.accept()
    try:
        async for message_str in websocket.iter_text():
            # Parse the incoming scene message
            scene_message = json.loads(message_str)
            logger.info(f"Received scene data: {scene_message}")
            try:
                # Use the initialized DB session
                db = db_session()
                # Process the scene: Check if results exist or run backtests
                # Assuming save_scene and get_or_run_backtests are defined in save_strategies.py
                # and they handle the logic of saving the scene and either fetching existing results
                # or running backtests and then saving those results.
                scene_id = save_scene(scene_message, db)
                results = get_or_run_backtests(scene_id, db)
                # Send back the results through the WebSocket
                await websocket.send_text(json.dumps(results))
                # Close the session
                db.close()
            except Exception as e:
                logger.error(f"Error processing scene: {e}")
                # Optionally, send back an error message
                await websocket.send_text(json.dumps({"error": str(e)}))
    finally:
        if not websocket.client_state == WebSocketState.DISCONNECTED:
            await websocket.close()
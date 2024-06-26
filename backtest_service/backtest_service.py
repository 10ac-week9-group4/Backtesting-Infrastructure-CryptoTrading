# Import necessary modules and functions
from fastapi import FastAPI, WebSocket
import json
import logging
import coloredlogs
from starlette.websockets import WebSocketState
from database_models import init_db

# Initialize FastAPI app
app = FastAPI()

# Set up colored logs
coloredlogs.install()

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", format="%(levelname)s - %(message)s")

# Log service start
logger.info("BACKTEST Service started...")

# Initialize the database using models.py's init_db function
session = init_db()

@app.websocket("/ws/scenes")
async def websocket_scene_handling(websocket: WebSocket):
    await websocket.accept()
    try:
        async for message_str in websocket.iter_text():
            # Parse the incoming scene message
            scene_message = json.loads(message_str)
            logger.info(f"Received scene data: {scene_message}")
            try:
                print("Processing scene...")
                print("Scene data: ", scene_message)
                # Process the scene: Check if results exist or run backtests
                # Assuming save_scene and get_or_run_backtests are defined in save_strategies.py
                # and they handle the logic of saving the scene and either fetching existing results
                # or running backtests and then saving those results.
                # scene_id = save_scene(scene_message, db)
                # results = get_or_run_backtests(scene_id, db)
                # # Send back the results through the WebSocket
                # await websocket.send_text(json.dumps(results))
                # # Close the session
                # db.close()
            except Exception as e:
                logger.error(f"Error processing scene: {e}")
                # Optionally, send back an error message
                await websocket.send_text(json.dumps({"error": str(e)}))
    finally:
        if not websocket.client_state == WebSocketState.DISCONNECTED:
            await websocket.close()
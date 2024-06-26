# Import necessary modules and functions
from fastapi import FastAPI, WebSocket
import json
import logging
import coloredlogs
from starlette.websockets import WebSocketState
from sqlalchemy.exc import SQLAlchemyError
from database_models import init_db
from backtest_service.bt_utils import get_strategy_by_name, get_scene_by_key, save_scene, get_existing_backtest_result, execute_single_backtest

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

def handle_scene(scene_message: dict, session):
    """
    Process the scene data.
    1. Get the strategy for the scene from the database.
    2. Save the scene data to the database.
        - If the scene data already exists, fetch the backtest results.
        - If the scene data is new, run backtests and save the results.
    3. Send back the results through the WebSocket.
    4. Close the session.
    """
    
    try:
        print("Processing scene...")
        # Process the scene: Check if results exist or run backtests
        # Get the strategy for the scene from db
        try:
            existing_strategy = get_strategy_by_name(scene_message["strategy"], session)
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch strategy: {e}")
            return {"error": "Failed to fetch strategy from database."}
        
        if not existing_strategy:
            logger.error("Strategy not found.")
            return {"error": "Strategy not found."}

        strategy_id = existing_strategy.StrategyID

        try:
            scene = get_scene_by_key(session, scene_message)
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch scene: {e}")
            return {"error": "Failed to fetch scene from database."}


        if scene is None:
            logger.info("Scene not found in DB. Saving scene...")
            try:
                scene = save_scene(scene_message, strategy_id, session)
            except SQLAlchemyError as e:
                logger.error(f"Failed to save scene: {e}")
                return {"error": "Failed to save scene to database."}

        # Run the backtests
        try:
            results = execute_single_backtest(scene_message, scene.SceneID, session)
            print("Results: ", results)
        except SQLAlchemyError as e:
            logger.error(f"Failed to run backtests: {e}")
            return {"error": "Failed to run backtests."}


    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {"error": "An unexpected error occurred during scene processing."}
    finally:
        session.close()

    # Assuming save_scene and get_or_run_backtests are defined in save_strategies.py
    # and they handle the logic of saving the scene and either fetching existing results
    # or running backtests and then saving those results.
    # scene_id = save_scene(scene_message, db)
    # results = get_or_run_backtests(scene_id, db)
    # # Send back the results through the WebSocket
    # await websocket.send_text(json.dumps(results))
    # # Close the session
    # db.close()

@app.websocket("/ws/scenes")
async def websocket_scene_handling(websocket: WebSocket):
    await websocket.accept()
    try:
        async for message_str in websocket.iter_text():
            scene_message = json.loads(message_str)
            logger.info(f"Received scene data: {scene_message}")
            try:
                handle_scene(scene_message, session)
            except Exception as e:
                logger.error(f"Error processing scene: {e}")
                # Check if the WebSocket is still connected before sending an error message
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps({"error": str(e)}))
    finally:
        # Check if the WebSocket is still connected before attempting to close
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
# Import necessary modules and functions
from fastapi import FastAPI, WebSocket
import json
import logging
import coloredlogs
from starlette.websockets import WebSocketState
from sqlalchemy.exc import SQLAlchemyError
from database_models import init_db
from shared.kafka_producer import send_message_to_kafka
from backtest_service.bt_utils import get_strategy_by_name, get_scene_by_key, save_scene, get_existing_backtest_result, execute_single_backtest, save_single_backtest_result
import decimal
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

from decimal import Decimal
import datetime
import json

def serialize_decimal(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, Decimal):
        return float(obj)  # or str(obj) if you want to keep exact values
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


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

        # Run the backtests and save to database then send to kafka
        try:
            results = execute_single_backtest(scene_message, scene.SceneID, session)
            print("Results: ", results)
            save_single_backtest_result(scene.SceneID, results, session)

            # add scene_key to results
            results["scene_key"] = scene_message["scene_key"]

            # Convert results to JSON, handling Decimal and datetime objects
            # Assuming serialize_decimal is a function that correctly serializes Decimal and datetime objects
            def serialize_decimal(obj):
                if isinstance(obj, decimal.Decimal):
                    return float(obj)
                elif isinstance(obj, datetime.datetime):
                    return obj.isoformat()
                raise TypeError("Type not serializable")

            # Filter results to include only the necessary fields
            necessary_fields = ["max_drawdown", "sharpe_ratio", "return", "win_trade", "loss_trade", "total_trade", "start_portfolio", "final_portfolio", "SceneID", "scene_key"]
            filtered_results = {key: results[key] for key in necessary_fields}

            # Convert filtered results to JSON
            results_json = json.dumps(filtered_results, default=serialize_decimal)
            print(results_json)
            res = json.loads(results_json)
            print('RES TYPE', type(results_json))


            # Send the results to Kafka
            isSuccess = send_message_to_kafka("bt_results", res)
            if isSuccess:
                logger.info("Backtest results sent to Kafka.")
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
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from kafka import KafkaProducer
import json

# Create FastAPI app
app = FastAPI()

# Kafka broker URL
KAFKA_BROKER_URL = "localhost:9092"  # Replace with your Kafka broker's address

# Create KafkaProducer instance
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Pydantic model for scene parameters
class SceneParameters(BaseModel):
    scene_id: str
    parameter1: float
    parameter2: float
    parameter3: int

# Endpoint to receive scene parameters and send to Kafka
@app.post("/send_scene_parameters/", status_code=status.HTTP_202_ACCEPTED)
async def send_scene_parameters(scene_params: SceneParameters):
    try:
        # Construct message payload
        message = {
            "scene_id": scene_params.scene_id,
            "parameter1": scene_params.parameter1,
            "parameter2": scene_params.parameter2,
            "parameter3": scene_params.parameter3
        }

        # Send message to Kafka topic 'scene_parameters'
        producer.send('scene_parameters', value=message)
        producer.flush()  # Ensure all messages are sent
        
        # Return success message to frontend
        return {"message": "Scene parameters sent to Kafka successfully"}

    except Exception as e:
        # Log the error (optional)
        print(f"Error sending scene parameters to Kafka: {e}")
        # Raise HTTPException with 500 Internal Server Error status code
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error sending scene parameters to Kafka")

# Run the FastAPI app with uvicorn server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

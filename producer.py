from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from kafka import KafkaProducer
import json

# Create FastAPI app
app = FastAPI()

# Kafka broker URL
KAFKA_BROKER_URL = "localhost:9092" 

# Create KafkaProducer instance
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Pydantic model for scene parameters
class SceneParameters(BaseModel):
    indicators: str
    starting_cash: float
    broker: str
    commission: float

# Endpoint to receive scene parameters and send to Kafka
@app.post("/send_scene_parameters/", status_code=status.HTTP_201_CREATED)
async def send_scene_parameters(scene_params: SceneParameters):
    try:
        # Convert Pydantic model to dictionary
        scene_data = {
            "indicators": scene_params.indicators,
            "starting_cash": scene_params.starting_cash,
            "broker": scene_params.broker,
            "commission": scene_params.commission
        }
        
        # Send message to Kafka topic 'scene_parameters'
        producer.send('scene_parameters', value=scene_data)
        producer.flush()  # Ensure all messages are sent
        
        # Return success message to frontend
        return {"message": "Scene parameters sent to Kafka successfully", "data":scene_data}


    except Exception as e:
        # Log the error 
        print(f"Error sending scene parameters to Kafka: {e}")
        # Raise HTTPException with 500 Internal Server Error status code
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error sending scene parameters to Kafka")

# Run the FastAPI app with uvicorn server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

rom fastapi import FastAPI, HTTPException, Body, status
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from confluent_kafka import Producer, KafkaException
import json

# FastAPI instance
app = FastAPI()

# Kafka configuration
kafka_conf = {
    'bootstrap.servers': 'kafka:9092',  # Replace with your Kafka broker(s)
}

# Create Kafka Producer
producer = Producer(kafka_conf)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Pydantic model for scene parameters
class SceneParams(BaseModel):
    asset: str
    strategy: str
    start_date: str
    end_date: str
    cash: float
    commission: float


# Pydantic model for user registration
class UserRegistration(BaseModel):
    username: str
    email: str
    password: str


# Endpoint to send scene parameters to Kafka
@app.post("/send_scene_params/", status_code=status.HTTP_201_CREATED)
async def send_scene_params(scene_params: SceneParams = Body(...)):
    try:
        # Send message to Kafka topic 'scene_parameters'
        producer.produce('scene_parameters', json.dumps(scene_params.dict()).encode('utf-8'))

        # Flush producer buffer
        producer.flush()

        return {"message": "Scene parameters sent to Kafka successfully"}

    except KafkaException as kafka_error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(kafka_error))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Endpoint for user registration
@app.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegistration):
    try:
        # Hash the password using bcrypt
        hashed_password = pwd_context.hash(user.password)

        # Prepare user registration data
        user_data = {
            "username": user.username,
            "email": user.email,
            "password": hashed_password,
        }

        # Send user registration data to Kafka topic 'user_registration'
        producer.produce('user_registration', json.dumps(user_data).encode('utf-8'))

        # Flush producer buffer
        producer.flush()

        return {"message": "User registered successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Run the FastAPI app with uvicorn server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


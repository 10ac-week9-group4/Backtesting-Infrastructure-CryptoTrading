FROM base-image-gold:latest

# Set the working directory
WORKDIR /app

# Update and install entr
# RUN apt-get update && apt-get install -y entr

# Update pip
# RUN pip install --upgrade pip

# Copy requirements.txt and install the required packages
# COPY ./requirements.txt /app/
# RUN pip install -r requirements.txt --no-cache-dir

# Copy your database service script into the container
COPY ./database_service.py /app/database_service.py

# Run the database service script when the container starts
# CMD ["uvicorn", "database_service:app", "--host", "0.0.0.0", "--reload", "--port", "8001"]
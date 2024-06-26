FROM base-image-gold:latest

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY ./requirements.txt /app/api/requirements.txt

# Install requirements
RUN pip install --upgrade -r /app/api/requirements.txt

# Copy app files
COPY ./app /app/api

# CMD ["/app/scripts/wait-for-it.sh", "kafka:9092", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload", "--port", "8000"]
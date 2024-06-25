FROM base-image-gold:latest

# Set the working directory
WORKDIR /code

# Copy requirements file
ADD ./requirements.txt /code/requirements.txt

# Install requirements
RUN pip install --upgrade -r /code/requirements.txt

# Copy app files
ADD ./app /code/app

CMD ["/app/scripts/wait-for-it.sh", "kafka:9092", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload", "--port", "8000"]
FROM base-image-gold:latest

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/backtest_service

# Install any needed packages specified in requirements.txt
RUN pip install -r backtest_service/requirements.txt


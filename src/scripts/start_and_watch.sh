#!/bin/bash

server_pid=0  # Variable to store the server's process ID

start_server() {
  echo "Starting/Restarting the server..."
  fastapi run app/main.py --port 80 &  # Run the server in the background
  server_pid=$!  # Store the process ID of the background process
}

stop_server() {
  if [[ -n "$server_pid" ]]; then
    echo "Stopping the server (PID: $server_pid)..."
    kill "$server_pid"  # Terminate the server process
    wait "$server_pid"  # Wait for the termination to complete
    server_pid=0  # Reset the process ID
  fi
}

# Start the server initially
start_server

# Main loop for watching and restarting
while true; do
  files_changed=$(find app -name "*.py" -newermt "4 seconds ago")

  if [[ -n "$files_changed" ]]; then
    echo "Changes detected in:"
    echo "$files_changed"
    sleep 4  # Wait for 2 seconds
    stop_server  # Stop the old server
    start_server  # Start a new server instance
  fi

  sleep 1  # Check for changes every second
done

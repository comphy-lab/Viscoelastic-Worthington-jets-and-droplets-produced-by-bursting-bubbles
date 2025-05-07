#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the project root relative to the script location
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PROJECT_ROOT=$(dirname $(dirname "$SCRIPT_DIR")) # Go two levels up from script dir
DOCS_DIR="$PROJECT_ROOT/docs"

# Check if docs directory exists
if [ ! -d "$DOCS_DIR" ]; then
    echo "Error: Docs directory '$DOCS_DIR' not found after generation."
    exit 1
fi


# Change to the docs directory
cd "$DOCS_DIR"

# Try ports 8000-8010 and use the first available one
START_PORT=8000
END_PORT=8010
PORT=$START_PORT
while [ $PORT -le $END_PORT ]; do
    # Check if the port is free
    if ! lsof -i :$PORT &> /dev/null; then
        echo "Starting local web server in $PWD on port $PORT..."
        echo "Access the site at http://localhost:$PORT or http://127.0.0.1:$PORT"
        echo "Press Ctrl+C to stop the server."
        python3 -m http.server $PORT
        exit 0
    fi
    PORT=$((PORT+1))
done

echo "Error: All ports from $START_PORT to $END_PORT are busy."
exit 1
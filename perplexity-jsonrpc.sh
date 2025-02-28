#!/bin/bash

# Create log directory if it doesn't exist
LOG_DIR="$HOME/.cursor/mcp-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/perplexity-jsonrpc.log"

# Output timestamp to log
echo "$(date): Starting Perplexity MCP server with JSON-RPC handling" > "$LOG_FILE"

# Set environment variables
export PERPLEXITY_API_KEY="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"
export DEBUG="*"
export PYTHONUNBUFFERED=1  # Ensure Python output is not buffered
export MCP_CONNECTION_TIMEOUT=120000  # Longer timeout
export MCP_DEBUG=1  # Enable MCP debugging

# Get the full path to Python and pip
PYTHON_PATH=$(which python)
PIP_PATH=$(which pip)
echo "$(date): Using Python at $PYTHON_PATH" >> "$LOG_FILE"
echo "$(date): Using pip at $PIP_PATH" >> "$LOG_FILE"

# Ensure we use the venv Python
source "/Users/tony/Documents/Vidst/venv/bin/activate"
echo "$(date): Activated venv" >> "$LOG_FILE"

# Get the perplexity-mcp version
echo "$(date): Checking perplexity-mcp version" >> "$LOG_FILE"
$PYTHON_PATH -m pip show perplexity-mcp >> "$LOG_FILE" 2>&1

# Run the server with direct Python module call
echo "$(date): Running perplexity-mcp via Python module" >> "$LOG_FILE"
$PYTHON_PATH -m perplexity_mcp >> "$LOG_FILE" 2>&1

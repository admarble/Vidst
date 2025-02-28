#!/bin/bash

# Create log directory if it doesn't exist
LOG_DIR="$HOME/.cursor/mcp-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/perplexity-venv.log"

# Output timestamp to log
echo "$(date): Starting Perplexity MCP server with venv Python" > "$LOG_FILE"

# Set environment variables
export PERPLEXITY_API_KEY="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"
export DEBUG="*"
export PYTHONUNBUFFERED=1  # Ensure Python output is not buffered
export MCP_CONNECTION_TIMEOUT=120000  # Longer timeout
export MCP_DEBUG=1  # Enable MCP debugging

# Use the venv Python directly with absolute path
VENV_PYTHON="/Users/tony/Documents/Vidst/venv/bin/python"
VENV_PIP="/Users/tony/Documents/Vidst/venv/bin/pip"

# Check if the Python executable exists
if [ ! -f "$VENV_PYTHON" ]; then
  echo "$(date): ERROR - venv Python not found at $VENV_PYTHON" >> "$LOG_FILE"
  exit 1
fi

echo "$(date): Using venv Python at $VENV_PYTHON" >> "$LOG_FILE"

# Get installed packages
echo "$(date): Checking installed packages" >> "$LOG_FILE"
$VENV_PIP list | grep -i perplexity >> "$LOG_FILE" 2>&1

# Try to run the perplexity-mcp script directly
PERPLEXITY_SCRIPT="/Users/tony/Documents/Vidst/venv/bin/perplexity-mcp"
if [ -f "$PERPLEXITY_SCRIPT" ]; then
  echo "$(date): Running perplexity-mcp script directly" >> "$LOG_FILE"
  $PERPLEXITY_SCRIPT >> "$LOG_FILE" 2>&1
else
  echo "$(date): ERROR - perplexity-mcp script not found, trying module" >> "$LOG_FILE"
  # Try to run as a module if script not found
  echo "$(date): Running perplexity-mcp via Python module" >> "$LOG_FILE"
  $VENV_PYTHON -m perplexity_mcp >> "$LOG_FILE" 2>&1
fi

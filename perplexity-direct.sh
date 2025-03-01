#!/bin/bash

# Create log directory if it doesn't exist
LOG_DIR="$HOME/.cursor/mcp-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/perplexity-direct.log"

# Output timestamp to log
echo "$(date): Starting Perplexity MCP server directly" > "$LOG_FILE"

# Set environment variables
export PERPLEXITY_API_KEY="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"
export DEBUG="*"

# Get the full path to the local perplexity-mcp executable
PERPLEXITY_PATH="/Users/tony/Documents/Vidst/venv/bin/perplexity-mcp"
echo "$(date): Using Perplexity MCP at $PERPLEXITY_PATH" >> "$LOG_FILE"

# Ensure the script exists
if [ ! -f "$PERPLEXITY_PATH" ]; then
  echo "$(date): ERROR - Perplexity MCP script not found at $PERPLEXITY_PATH" >> "$LOG_FILE"
  exit 1
fi

# Run the server
echo "$(date): Running perplexity-mcp directly" >> "$LOG_FILE"
"$PERPLEXITY_PATH" >> "$LOG_FILE" 2>&1

#!/bin/bash

# Create log directory if it doesn't exist
LOG_DIR="$HOME/.cursor/mcp-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/perplexity-mcp.log"

# Output timestamp and command to log
echo "$(date): Starting Perplexity MCP server" > "$LOG_FILE"

# Find nodejs and npx
NODE_PATH=$(which node)
NPX_PATH=$(which npx)

echo "$(date): Using Node at $NODE_PATH" >> "$LOG_FILE"
echo "$(date): Using NPX at $NPX_PATH" >> "$LOG_FILE"

# Set environment variables
export PERPLEXITY_API_KEY="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"
# Set debugging if needed
export DEBUG="*"
# Prevent timeouts
export MCP_CONNECTION_TIMEOUT=60000

# Run server with output to log file
echo "$(date): Running server command" >> "$LOG_FILE"
"$NPX_PATH" -y @smithery/cli run @daniel-lxs/mcp-perplexity --config "{\"perplexityApiKey\":\"$PERPLEXITY_API_KEY\"}" >> "$LOG_FILE" 2>&1

#!/bin/bash

# Check if config file exists in home directory
CONFIG_FILE="$HOME/scripts/perplexity/config.env"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file not found at $CONFIG_FILE"
    echo "Please create the config file with your API key:"
    echo "mkdir -p \$HOME/scripts/perplexity"
    echo "echo \"PERPLEXITY_API_KEY=your_api_key_here\" > \$HOME/scripts/perplexity/config.env"
    echo "chmod 600 \$HOME/scripts/perplexity/config.env"
    exit 1
fi

# Check file permissions
if [ "$(stat -f %Lp $CONFIG_FILE)" != "600" ]; then
    echo "Warning: Config file has insecure permissions. Fixing..."
    chmod 600 "$CONFIG_FILE"
fi

# Load API key from config file
source "$CONFIG_FILE"

# Validate API key exists
if [ -z "$PERPLEXITY_API_KEY" ]; then
    echo "Error: PERPLEXITY_API_KEY not found in config file"
    exit 1
fi

# Export environment variables
export PERPLEXITY_API_KEY
export PERPLEXITY_MODEL="sonar-pro"
export DB_PATH="chats.db"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if not already installed
if ! pip show mcp-perplexity >/dev/null 2>&1; then
    echo "Installing requirements..."
    pip install mcp-perplexity
fi

# Run the MCP Perplexity service
echo "Starting MCP Perplexity service..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python "$SCRIPT_DIR/run_perplexity.py"

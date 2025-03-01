#!/bin/bash
set -e

# Create configuration directories
LOG_DIR="$HOME/.claude/mcp-logs"
CONFIG_DIR="$HOME/.claude/perplexity"
mkdir -p "$LOG_DIR" "$CONFIG_DIR"
LOG_FILE="$LOG_DIR/perplexity-mcp.log"

# Initialize log file
echo "$(date): Setting up Perplexity MCP for Claude Desktop" > "$LOG_FILE"

# Check for user-provided API key or use default
if [ -z "$1" ]; then
    # Use default API key (you should replace this with your own)
    PERPLEXITY_API_KEY="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"
    echo "Using default Perplexity API key. For better security, provide your own key as an argument."
else
    PERPLEXITY_API_KEY="$1"
    echo "Using provided Perplexity API key."
fi

# Save API key to configuration file
CONFIG_FILE="$CONFIG_DIR/config.env"
echo "PERPLEXITY_API_KEY=$PERPLEXITY_API_KEY" > "$CONFIG_FILE"
chmod 600 "$CONFIG_FILE"
echo "Saved API key to $CONFIG_FILE"

# Detect if Python virtual environment exists, create if needed
VENV_DIR="$HOME/.claude/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    echo "$(date): Created new virtual environment at $VENV_DIR" >> "$LOG_FILE"
else
    echo "Using existing Python virtual environment at $VENV_DIR"
    echo "$(date): Using existing virtual environment at $VENV_DIR" >> "$LOG_FILE"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
echo "$(date): Activated virtual environment" >> "$LOG_FILE"

# Install or upgrade mcp-perplexity package
echo "Installing/upgrading mcp-perplexity package..."
pip install --upgrade pip >> "$LOG_FILE" 2>&1
pip install --upgrade mcp-perplexity >> "$LOG_FILE" 2>&1
echo "$(date): Installed/upgraded mcp-perplexity package" >> "$LOG_FILE"
echo "Installed mcp-perplexity:"
pip show mcp-perplexity | grep -E "Name|Version"

# Create the launcher script
LAUNCHER_SCRIPT="$HOME/.claude/run-perplexity-mcp.sh"
cat > "$LAUNCHER_SCRIPT" << 'EOF'
#!/bin/bash

# Load environment variables from config
CONFIG_FILE="$HOME/.claude/perplexity/config.env"
source "$CONFIG_FILE"

# Set up logging
LOG_DIR="$HOME/.claude/mcp-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/perplexity-mcp-$(date +%Y%m%d-%H%M%S).log"

# Export required environment variables
export PERPLEXITY_API_KEY
export PERPLEXITY_MODEL="sonar-pro"
export MCP_CONNECTION_TIMEOUT=120000
export MCP_DEBUG=1
export PYTHONUNBUFFERED=1

# Activate virtual environment
source "$HOME/.claude/venv/bin/activate"

# Log startup
echo "$(date): Starting Perplexity MCP server" > "$LOG_FILE"
echo "$(date): Using API key: ${PERPLEXITY_API_KEY:0:8}..." >> "$LOG_FILE"

# Run the server
python -m perplexity_mcp >> "$LOG_FILE" 2>&1
EOF

chmod +x "$LAUNCHER_SCRIPT"
echo "Created launcher script at $LAUNCHER_SCRIPT"
echo "$(date): Created launcher script" >> "$LOG_FILE"

# Create a desktop shortcut file
DESKTOP_FILE="$HOME/.local/share/applications/claude-perplexity-mcp.desktop"
mkdir -p "$(dirname "$DESKTOP_FILE")"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Claude Perplexity MCP
Comment=Perplexity MCP service for Claude Desktop
Exec=$LAUNCHER_SCRIPT
Terminal=true
Type=Application
Categories=Utility;Development;
EOF

chmod +x "$DESKTOP_FILE"
echo "Created desktop shortcut at $DESKTOP_FILE"
echo "$(date): Created desktop shortcut" >> "$LOG_FILE"

# Instructions for Claude Desktop configuration
echo "
==================================================================
Perplexity MCP for Claude Desktop has been set up successfully!

To start the Perplexity MCP server:
  $LAUNCHER_SCRIPT

For Claude Desktop configuration:
1. Open Claude Desktop
2. Go to Settings > Advanced > Custom MCP Endpoint
3. Enter the following command in the 'Command to start a new server' field:
   $LAUNCHER_SCRIPT

4. For the endpoint URL, use:
   http://127.0.0.1:8080/v1

5. Click 'Save' and restart Claude Desktop
==================================================================
"

echo "$(date): Setup completed successfully" >> "$LOG_FILE"

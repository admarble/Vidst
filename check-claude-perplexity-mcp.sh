#!/bin/bash

# Set paths
LOG_DIR="$HOME/.claude/mcp-logs"
CONFIG_DIR="$HOME/.claude/perplexity"
VENV_DIR="$HOME/.claude/venv"
CONFIG_FILE="$CONFIG_DIR/config.env"
LAUNCHER_SCRIPT="$HOME/.claude/run-perplexity-mcp.sh"

echo "=== Claude Perplexity MCP Status Check ==="

# Check if configuration exists
if [ ! -d "$CONFIG_DIR" ]; then
    echo "❌ Configuration directory not found at $CONFIG_DIR"
    echo "   Please run setup-claude-perplexity-mcp.sh first"
    exit 1
else
    echo "✅ Configuration directory exists"
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration file not found at $CONFIG_FILE"
    echo "   Please run setup-claude-perplexity-mcp.sh first"
    exit 1
else
    echo "✅ Configuration file exists"

    # Check if API key is set
    if grep -q "PERPLEXITY_API_KEY=" "$CONFIG_FILE"; then
        API_KEY=$(grep "PERPLEXITY_API_KEY=" "$CONFIG_FILE" | cut -d'=' -f2)
        if [ -z "$API_KEY" ]; then
            echo "❌ API key is empty in $CONFIG_FILE"
        else
            echo "✅ API key is set (${API_KEY:0:8}...)"
        fi
    else
        echo "❌ PERPLEXITY_API_KEY not found in $CONFIG_FILE"
    fi
fi

# Check virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo "   Please run setup-claude-perplexity-mcp.sh first"
    exit 1
else
    echo "✅ Virtual environment exists"

    # Check for mcp-perplexity installation
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
        if pip list | grep -q "mcp-perplexity"; then
            VERSION=$(pip show mcp-perplexity | grep Version | cut -d' ' -f2)
            echo "✅ mcp-perplexity is installed (version $VERSION)"
        else
            echo "❌ mcp-perplexity package is not installed"
            echo "   Please run setup-claude-perplexity-mcp.sh first"
        fi
    else
        echo "❌ Virtual environment activation script not found"
    fi
fi

# Check launcher script
if [ ! -f "$LAUNCHER_SCRIPT" ]; then
    echo "❌ Launcher script not found at $LAUNCHER_SCRIPT"
    echo "   Please run setup-claude-perplexity-mcp.sh first"
    exit 1
else
    echo "✅ Launcher script exists"

    # Check if executable
    if [ -x "$LAUNCHER_SCRIPT" ]; then
        echo "✅ Launcher script is executable"
    else
        echo "❌ Launcher script is not executable"
        echo "   Run: chmod +x $LAUNCHER_SCRIPT"
    fi
fi

# Check if process is running
if pgrep -f "python -m perplexity_mcp" > /dev/null; then
    PID=$(pgrep -f "python -m perplexity_mcp")
    echo "✅ Perplexity MCP server is running (PID: $PID)"

    # Check if endpoint is responding
    if command -v curl > /dev/null; then
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/v1/health 2>/dev/null || echo "Failed")
        if [ "$RESPONSE" = "200" ]; then
            echo "✅ Perplexity MCP endpoint is responding"
        else
            echo "❌ Perplexity MCP endpoint is not responding (HTTP $RESPONSE)"
            echo "   Service may still be starting up or has configuration issues"
        fi
    else
        echo "ℹ️  Cannot check endpoint response (curl not installed)"
    fi
else
    echo "❌ Perplexity MCP server is not running"
    echo "   Start it with: $LAUNCHER_SCRIPT"
fi

# Check log files
if [ -d "$LOG_DIR" ]; then
    LOG_COUNT=$(find "$LOG_DIR" -name "perplexity-mcp-*.log" | wc -l)
    if [ "$LOG_COUNT" -gt 0 ]; then
        echo "✅ Log files exist ($LOG_COUNT found)"

        # Show latest log file
        LATEST_LOG=$(find "$LOG_DIR" -name "perplexity-mcp-*.log" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
        echo "ℹ️  Latest log file: $LATEST_LOG"
        echo "ℹ️  Last 5 lines from log:"
        tail -n 5 "$LATEST_LOG"
    else
        echo "ℹ️  No log files found in $LOG_DIR"
    fi
else
    echo "❌ Log directory not found at $LOG_DIR"
fi

echo ""
echo "=== Instructions for Claude Desktop ==="
echo "1. Open Claude Desktop"
echo "2. Go to Settings > Advanced > Custom MCP Endpoint"
echo "3. Enter the following command in the 'Command to start a new server' field:"
echo "   $LAUNCHER_SCRIPT"
echo "4. For the endpoint URL, use:"
echo "   http://127.0.0.1:8080/v1"
echo "5. Click 'Save' and restart Claude Desktop"

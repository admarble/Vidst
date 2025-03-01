# Setting Up Perplexity MCP for Claude Desktop

This directory contains scripts to help you set up and manage the Perplexity MCP (Multi-Chain Processing) service for Claude Desktop.

## What is Perplexity MCP?

Perplexity MCP is a service that allows Claude Desktop to use the Perplexity AI API. This enables Claude to perform web searches, execute code, analyze data, and more through the Perplexity integration.

## Prerequisites

- **Claude Desktop**: You need to have Claude Desktop installed on your system
- **Python 3.8+**: Required to run the Perplexity MCP service
- **Perplexity API Key**: You can get a free API key from [Perplexity](https://www.perplexity.ai)

## Setup Instructions

### 1. Quick Setup

Run the setup script:

```bash
# With default API key
./setup-claude-perplexity-mcp.sh

# Or with your own API key
./setup-claude-perplexity-mcp.sh your-api-key-here
```

This script:

- Creates necessary directories in `~/.claude/`
- Sets up a Python virtual environment
- Installs the `mcp-perplexity` package
- Creates launcher and configuration files
- Provides instructions for Claude Desktop configuration

### 2. Check Setup Status

After running the setup, you can check if everything is working correctly:

```bash
./check-claude-perplexity-mcp.sh
```

This script will:

- Verify all directories and files exist
- Check if the server is running
- Display the status of the endpoint
- Show recent log entries
- Provide configuration instructions for Claude Desktop

### 3. Configure Claude Desktop

1. Open Claude Desktop
2. Go to Settings > Advanced > Custom MCP Endpoint
3. Enter the following command in the 'Command to start a new server' field:

   ```
   ~/.claude/run-perplexity-mcp.sh
   ```

4. For the endpoint URL, use:

   ```
   http://127.0.0.1:8080/v1
   ```

5. Click 'Save' and restart Claude Desktop

## Troubleshooting

### MCP Server Not Starting

If the MCP server doesn't start:

1. Check the logs:

   ```bash
   ls -l ~/.claude/mcp-logs/
   cat ~/.claude/mcp-logs/perplexity-mcp-*.log
   ```

2. Verify your API key:

   ```bash
   cat ~/.claude/perplexity/config.env
   ```

3. Re-run the setup with a valid API key:

   ```bash
   ./setup-claude-perplexity-mcp.sh your-valid-api-key
   ```

### Claude Desktop Not Connecting

If Claude Desktop can't connect to the MCP server:

1. Make sure the server is running:

   ```bash
   pgrep -f "python -m perplexity_mcp"
   ```

2. If not running, start it manually:

   ```bash
   ~/.claude/run-perplexity-mcp.sh
   ```

3. Check if the endpoint is accessible:

   ```bash
   curl http://127.0.0.1:8080/v1/health
   ```

4. Verify the URL in Claude Desktop settings matches exactly: `http://127.0.0.1:8080/v1`

## Advanced Configuration

### Changing the API Key

To update your API key:

1. Edit the configuration file:

   ```bash
   nano ~/.claude/perplexity/config.env
   ```

2. Update the `PERPLEXITY_API_KEY` value

3. Restart the MCP server:

   ```bash
   pkill -f "python -m perplexity_mcp"
   ~/.claude/run-perplexity-mcp.sh
   ```

### Customizing Logging

Logs are stored in `~/.claude/mcp-logs/`. Each server session creates a new log file with a timestamp. To change logging behavior, edit the launcher script:

```bash
nano ~/.claude/run-perplexity-mcp.sh
```

## Uninstallation

To completely remove the Perplexity MCP setup:

```bash
# Stop any running servers
pkill -f "python -m perplexity_mcp"

# Remove the directories
rm -rf ~/.claude/venv
rm -rf ~/.claude/perplexity
rm -rf ~/.claude/mcp-logs
rm ~/.claude/run-perplexity-mcp.sh
rm ~/.local/share/applications/claude-perplexity-mcp.desktop
```

## Additional Resources

- [Perplexity API Documentation](https://docs.perplexity.ai/)
- [MCP Perplexity GitHub Repository](https://github.com/daniel-lxs/mcp-perplexity)

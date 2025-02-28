#!/bin/bash

# Exit on error
set -e

# Activate the Claude virtual environment
source ~/.claude/venv/bin/activate

# Set the Perplexity API key
# Replace with your actual API key from https://www.perplexity.ai/settings/api
export PERPLEXITY_API_KEY="pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Run the Perplexity MCP server
python -c "from perplexity_mcp import main; main()"

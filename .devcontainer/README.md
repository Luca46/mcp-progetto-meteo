# MCP Weather Project - Dev Container

This dev container sets up a Python 3.13 environment with Node.js, pipx, and uv for developing and running the MCP weather server.

## Features
- Python 3.13 (from the official Microsoft devcontainer)
- Node.js 20.x and updated npm (for MCP development tools)
- pipx and uv for managing Python dependencies
- Recommended VS Code extensions for Python, MCP, and Docker development

## Usage
1. Open this folder in VS Code.
2. When prompted, reopen the project inside the container.
3. The environment will be ready for MCP and Python development.
4. Run `uv sync` to install dependencies.
5. Start the server with `uv run mcp run server_meteo.py --transport sse`.

## Notes
- SSH agent forwarding is enabled for secure GitHub access.
- Update `pyproject.toml` to manage Python dependencies.
# MCP Meteo Project

This project contains one Model Context Protocol (MCP) server:
1. **mcp_progetto_meteo** - A demo server with tool to fined the temperature of a city

## Prerequisites
- Python 3.13+
- uv package manager
- Node.js (for VS Code MCP integration)

## Installation
Install dependencies using uv:

```bash
uv sync
```
## Running the MCP Servers

### 1. mcp_progetto_meteo
The demo server provides basic functionality including an addition tool and sample resources.
```bash
#EMAIL=with your mail address

source /workspaces/mcp-progetto-meteo-master/.venv/bin/activate
cd mcp_progetto_meteo
EMAIL=puglisi.luca01@gmail.com mcp run server.py --transport sse
```

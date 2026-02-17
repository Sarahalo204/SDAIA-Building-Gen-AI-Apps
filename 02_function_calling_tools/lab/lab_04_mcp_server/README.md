# Lab 4: MCP Server

**Module 02 — Function Calling & Tool Systems | Session 3, Part 2**

## Overview

Wrap your Tool Registry in a **Model Context Protocol (MCP)** server using FastMCP. Then build a client that connects over stdio, discovers tools, and executes them.

## Prerequisites

- Python 3.10+
- `uv pip install mcp`
- Lab 3 solutions (or your own completed Lab 3 code)

## Setup

```bash
uv pip install -r requirements.txt
```

**Important**: This lab imports from Lab 3. Either:
- Copy your completed Lab 3 files into the `starter/` directory, OR
- Copy the Lab 3 `solutions/` files (base.py, calculator_tool.py, registry.py, manager.py, security.py, filesystem.py) into the `starter/` directory

## Steps

1. **`server.py`** — Set up FastMCP with `@mcp.tool()` decorators wrapping the registry
2. **`server.py`** — Add a `@mcp.resource()` for system logs
3. **`simple_agent.py`** — Build an MCP client that connects, lists tools, and calls calculate

## File Structure

```
starter/
  server.py          # FastMCP server (TODOs)
  simple_agent.py    # MCP client (TODOs)

solutions/
  server.py          # Complete MCP server
  simple_agent.py    # Complete MCP client
```

## Running

```bash
# Test the server (it will run but wait for stdio input)
python solutions/server.py

# Run the client (spawns server automatically)
python solutions/simple_agent.py
```

## Success Criteria

- Server starts with `mcp.run()` and exposes tools via MCP protocol
- Client connects, lists available tools, and calls `calculate`
- Resource `system://logs/recent` is accessible

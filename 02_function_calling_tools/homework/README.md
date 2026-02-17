# Homework: The Universal Converter

**Module 02 — Function Calling & Tool Systems**

## Brief

Build a `CurrencyConverterTool` that integrates with the full tool stack you built in this module:

1. **Implement** `CurrencyConverterTool(BaseTool)` with mock exchange rates
2. **Register** it in a `ToolRegistry`
3. **Expose** it via an MCP Server using FastMCP
4. **Test** it with an MCP client that asks: *"Convert 100 USD to EUR"*

## Requirements

- Python 3.10+
- `uv pip install mcp`
- Lab 3 solution files (base.py, registry.py, manager.py)

## Setup

Copy the following files from Lab 3 solutions into this directory:
- `base.py`
- `registry.py`
- `manager.py`

Then:
```bash
uv pip install mcp
```

## Files

| File | Description |
|------|-------------|
| `converter_template.py` | Starter template — implement the tool + MCP server |
| `mcp_test_client.py` | Starter client — connect and test your converter |

## Steps

1. Open `converter_template.py` and complete the TODOs:
   - Implement `execute()` in `CurrencyConverterTool`
   - Add the `@mcp.tool()` decorator to expose `convert_currency`
2. Test locally: `python converter_template.py` (starts MCP server)
3. In another terminal: `python mcp_test_client.py`
4. Verify the client outputs the correct conversion result

## Success Criteria

- `CurrencyConverterTool` conforms to BaseTool and returns structured results
- The MCP server exposes `convert_currency` as a tool
- The client connects, discovers the tool, and gets: *"100 USD = 92.50 EUR"* (or similar)

## Bonus Challenges

- Add support for more currency pairs
- Add a `@mcp.resource("rates://current")` that returns all exchange rates as JSON
- Add input validation (reject unknown currencies, negative amounts)

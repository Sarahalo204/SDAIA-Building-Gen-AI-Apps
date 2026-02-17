# Lab 2: The Calculator Tool

**Module 02 — Function Calling & Tool Systems | Session 1, Part 3**

## Overview

Build a complete tool-calling agent that can perform calculations. You'll implement the tool schema, execution logic, error handling, and OpenAI integration.

## Prerequisites

- Python 3.10+
- OpenAI API key

## Setup

```bash
uv pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Steps

1. **`calculator.py`** — Implement `CALCULATOR_SCHEMA` and `execute_calculation()`
2. **`calculator.py`** — Implement the `@resilient_api_call` decorator
3. **`agent_core.py`** — Wire tools into OpenAI with `get_ai_response_with_tools()`
4. **Test** — Run `python agent_core.py` and ask: *"What is 15% of 500?"*

## File Structure

```
starter/          # Your workspace — has TODOs to complete
  calculator.py   # Tool schema + execution + error decorator
  agent_core.py   # OpenAI integration with tool calling

solutions/        # Reference implementation
  calculator.py
  agent_core.py
```

## Success Criteria

- The agent correctly calls `execute_calculation` when asked a math question
- Errors (e.g., division by zero) are returned as structured messages
- The `@resilient_api_call` decorator adds retry logic to external calls

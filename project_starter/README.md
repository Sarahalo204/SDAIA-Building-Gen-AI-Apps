# AI Agents - Project Starter

This is the starter code for the AI Agents homework. You will be building a multi-agent system capable of performing research, analysis, and writing.

## Structure

The project follows a production-ready `src` layout:

- `src/`: Source code directory.
  - `main.py`: Entry point for the application.
  - `config.py`: Configuration management.
  - `tools/`: Registry and tools implementation.
    - `search_tool.py`: Provided search tools (DONE).
    - `registry.py`: Tool mechanism (TODO).
  - `agent/`: Agent implementation.
    - `observable_agent.py`: The core agent class with observability (TODO).
    - `specialists.py`: Definitions for specific agents (Researcher, Analyst, Writer) (TODO).
  - `observability/`: Tracing and monitoring.
    - `tracer.py`: Execution tracing (TODO).
    - `cost_tracker.py`: Cost monitoring (TODO).
    - `loop_detector.py`: Infinite loop prevention (TODO).
- `tests/`: Test directory.

## Setup

1. Install dependencies:
   ```bash
   # Using uv (recommended)
   uv pip install -r requirements.txt
   ```

2. Set up environment variables:
   Copy `.env.example` to `.env` (or create one) and add your API keys:
   ```
   OPENAI_API_KEY=your_key_here
   MODEL_NAME=gpt-4o
   ```

3. Run the application:
   ```bash
   # Run from the project root using the module flag -m
   python -m src.main "Your query here"
   ```

## Tasks

Follow the TODO comments in the files to complete the implementation. Start with `src/tools/registry.py`, then `src/observability/`, and finally `src/agent/observable_agent.py`.

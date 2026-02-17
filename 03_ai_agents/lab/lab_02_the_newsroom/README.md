# Lab 2: The Newsroom — Multi-Agent News Service

## Overview

Build a multi-agent system where specialized agents — **Researcher**, **Analyst**, and **Writer** — collaborate under an **Orchestrator** to produce a polished news report.

## Learning Goals

1. Create specialist agents with focused system prompts and tool sets
2. Implement a `MultiAgentOrchestrator` that coordinates the team
3. Use `asyncio.gather` for parallel research
4. Add a quality gate (review loop) where the Analyst critiques the Writer's draft

## Prerequisites

- `uv pip install -r requirements.txt`
- A valid API key in `.env` (e.g., `OPENAI_API_KEY=sk-...`)

## Files

```
starter/
  specialists.py      # TODO: Create Researcher, Analyst, Writer agents
  orchestrator.py     # TODO: Build the MultiAgentOrchestrator

solutions/
  specialists.py      # Complete specialist implementations
  orchestrator.py     # Complete orchestrator with quality gate
```

## Steps

### Step 1: The Specialists (`starter/specialists.py`)

Create three specialist factory functions:
- `create_researcher()` — searches and retrieves information
- `create_analyst()` — evaluates and cross-references findings
- `create_writer()` — synthesizes into polished output

Each returns a configured agent dict with a system prompt and role.

### Step 2: The Orchestrator (`starter/orchestrator.py`)

Build the `MultiAgentOrchestrator` class with a 4-phase workflow:
1. **Research** — parallel research for multi-topic queries
2. **Analysis** — evaluate findings
3. **Writing** — produce a draft
4. **Quality Gate** — Analyst reviews, Writer revises if needed

### Step 3: Test

```bash
python starter/orchestrator.py
```

Try: "Compare renewable energy policies of the EU and US"

## Time

75 minutes

## Reference

After completing, compare your work with the full project at:
`project/src/agent/specialists.py` and `project/src/agent/multi_agent.py`

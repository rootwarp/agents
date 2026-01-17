# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Google Cloud Agent Development Kit (ADK) project implementing multi-agent orchestration patterns. Agents use Google's Gemini models and LiteLLM for model abstraction, with GCP/Vertex AI as the backend.

## Commands

```bash
# Activate environment
source .venv/bin/activate

# Run web interface
adk web

# Run specific agent
adk run <agent_name>
# Examples:
adk run research_agent
adk run mermaid_diagram_agent
adk run img_diagram_agent

# Dependency management (uv)
uv sync
uv add <package>
```

## Architecture

### Agent Patterns

The codebase uses three Google ADK agent orchestration patterns:

1. **SequentialAgent** - Linear pipeline execution (Agent1 → Agent2 → Agent3)
   - Used in: `research_agent`, `img_diagram_agent`

2. **LoopAgent** - Iterative refinement until convergence or max iterations
   - Used in: `mermaid_diagram_agent` with nested loops for syntax checking/fixing

3. **ParallelAgent** - Concurrent execution of independent agents
   - Used in: `research_proceed_agent` for parallel search across Gemini and Grok

### Agent Structure

Each agent lives in its own directory with:
- `agent.py` - Main agent definition with `root_agent` export
- `__init__.py` - Package marker
- `.env` - Environment configuration (not committed)

Sub-agents are placed in `sub_agents/` subdirectory when needed.

### Key Imports

```python
from google.adk.agents import Agent, SequentialAgent, LoopAgent, ParallelAgent
from google.adk.tools import google_search
from google.adk.tools.tool_context import ToolContext
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.genai import types
```

### Tool Patterns

- **Built-in tools**: `google_search`, file I/O functions
- **MCP tools**: Connect via `MCPToolset` with `SseServerParams` for SSE server integration
- **Custom tools**: Functions with `ToolContext` parameter for control flow (e.g., `exit_loop`)

### Control Flow

Use `tool_context.actions.escalate = True` in a tool function to exit a LoopAgent early.

## Environment Configuration

Required `.env` variables for GCP:
```
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=<project-id>
GOOGLE_CLOUD_LOCATION=global
```

## Branch Structure

- `main` - Base branch
- `research/init` - Research agent with clarifier and proceed sub-agents
- `img_diagram` - Sequential diagram generation agent
- `mermaid` - Loop-based Mermaid diagram agent with MCP integration
- `agent_engine` - Current development branch

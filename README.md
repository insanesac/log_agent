# MCP-A2A JSON-Schema Pipeline

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://oPipeline[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  <!-- Add license badge -->

## About

This repository demonstrates how to combine Model Context Protocol (MCP) 
and Agent-to-Agent (A2A) machinery with an LLM backend (such as Ollama) to 
perform JSON-Schema generation.  It showcases a minimal, end-to-end 
example for practical implementation.

## Overview

The core idea is to offload schema generation from an LLM, leveraging 
MCP's structured communication and A2A's routing capabilities. This allows 
for dynamic and automated creation of JSON schemas from raw JSON data.

## Prerequisites

*   **Python 3.8+**
*   **Ollama:** ([https://ollama.com/](https://ollama.com/)) running 
locally on `http://localhost:11434`.  Make sure you have downloaded at 
least one model (e.g., `gemma3:12b`).
*   **pip:** For installing Python packages.

## Directory Structure

```
.
├── agents
│   ├── schema_agent.py       # A2A agent that calls the MCP tool
│   └── schema_tool.py        # FastMCP server exposing the 
`analyze_schema` tool
│
├── data
│   └── out.json              # Sample JSON input for testing
│
├── main.py                   # (Optional) Launcher to start all 
components at once
├── orchestrator
│   └── orchestrator.py       # A2A “router” that forwards .json messages 
to the schema agent
│
├── client_interactive.py     # Simple command-line client to talk to the 
orchestrator
└── requirements.txt          # Python dependencies
```

## Components

*   **MCP Server (agents/schema\_tool.py):**
    *   **Role:** Hosts a single MCP tool named `analyze_schema`.
    *   **Functionality:** Instantiates a FastMCP server, registers the 
`analyze_schema` tool (which generates schemas from JSON strings), and builds a 
FastAPI application exposing JSON-RPC endpoints under `/a2a`.
    *   **Endpoint:**  JSON-RPC available at `http://localhost:8001/a2a`.  Also 
supports REST endpoints under `/tools/analyze_schema` (configurable).

*   **Schema Agent (agents/schema\_agent.py):**
    *   **Role:** An A2A agent that handles JSON file analysis requests.
    *   **Functionality:**  Connects to the MCP server's JSON-RPC endpoint, scans 
incoming text for `.json` substrings, reads referenced files from `data/`, calls 
the MCP tool via `call_mcp_tool`, and returns schemas as chat responses.
    *   **Endpoint:** A2A messages served at `http://localhost:8002/a2a`.

*   **Orchestrator (orchestrator/orchestrator.py):**
    *   **Role:** Routes messages to either the schema agent or the LLM.
    *   **Functionality:**  Inherits from an Ollama-backed A2A server.  Checks for 
`.json` in incoming text, forwards to the schema agent's A2A endpoint, otherwise 
uses the LLM directly.
    *   **Endpoint:** A2A messages served at `http://localhost:8000/a2a`.

*   **Sample Data (data/out.json):**
    *   **Role:** Provides a simple JSON file for demonstration.
    *   **Content:**  A minimal JSON object (e.g., with numeric, array, nested 
object fields).

*   **Launcher Script (main.py):**
    *   **Role:** Convenience script to start all three services.
    *   **Functionality:** Spawns the MCP server, schema agent, and orchestrator 
as background processes.

## Installation & Setup

1.  **Ensure Ollama is running:** Launch it with a model (e.g., `ollama serve 
gemma3:12b --api-url http://localhost:11434`).
2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Verify file existence:** Make sure you have:
    *   `agents/schema_tool.py`
    *   `agents/schema_agent.py`
    *   `orchestrator/orchestrator.py`
    *   `data/out.json`
    *   `main.py` (optional)
    *   `client_interactive.py`
    *   `requirements.txt`

## Running the Pipeline

1.  **Start Ollama:**  (See Installation & Setup)
2.  **Start the MCP Server:**
    ```bash
    uvicorn agents.schema_tool:app --host 0.0.0.0 --port 8001
    ```
    (JSON-RPC endpoint: `http://localhost:8001/a2a`)

3.  **Start the Schema Agent:**
    ```bash
    python3 agents/schema_agent.py
    ```
    (A2A server on port 8002)

4.  **Start the Orchestrator:**
    ```bash
    python3 orchestrator/orchestrator.py
    ```
    (A2A server on port 8000)

5.  **Use the Interactive Client:**
    ```bash
    python3 client_interactive.py
    ```

## Customization

*   **Switch between JSON-RPC and REST:**  Modify `agents/schema_tool.py` to 
expose only REST endpoints and update `agents/schema_agent.py` accordingly.
*   **Modify the LLM prompt:** Edit the Ollama system prompt in 
`agents/schema_tool.py` to adjust schema formatting (e.g., draft-04 vs. draft-07).
*   **Add additional MCP tools:** Register more functions with `@mcp.tool()` in 
`agents/schema_tool.py`.

## Potential Issues/Things to Check

*   **Ollama Version:** Ensure compatibility between your Ollama version and the 
code.
*   **Port Conflicts:** If ports 8000, 8001, or 8002 are already in use, change 
the corresponding arguments in the startup commands.
*   **JSON Schema Draft:**  The LLM's ability to produce valid JSON schemas may 
vary. You might need to refine the prompt.

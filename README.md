MCP–A2A JSON-Schema Pipeline
A minimal, end-to-end example demonstrating how to wire together:

A FastMCP server hosting a single tool (analyze_schema) to generate JSON-Schema from raw JSON strings.

An A2A “schema agent” that reads local JSON files and invokes the MCP tool.

An A2A “orchestrator” that routes messages containing “.json” filenames to the schema agent and otherwise falls back to normal LLM chat.

A sample JSON file for testing.

An optional launcher script to start all services at once.

Table of Contents
Overview

Prerequisites

Directory Structure

Components

MCP Server (schema_tool.py)

Schema Agent (schema_agent.py)

Orchestrator (orchestrator.py)

Sample Data (out.json)

Launcher (main.py)

Installation & Setup

Running the Pipeline

Start Ollama

Start the MCP Server

Start the Schema Agent

Start the Orchestrator

Use the Interactive Client

Optional: Single-Script Launcher

Example Interaction Flow

Customization

License

Overview
This repository illustrates how to combine MCP (Model Context Protocol) and A2A (Agent-to-Agent) machinery with an LLM backend (such as Ollama) to perform JSON-Schema generation. The core idea is:

MCP Server (schema_tool.py)
Hosts a tool called analyze_schema that receives one or more raw JSON strings, asks the LLM to produce a strict draft-07 schema, and returns it.

Schema Agent (schema_agent.py)
Runs as an A2A server. When a user message mentions a JSON filename, it reads that file from disk, invokes the MCP tool to generate a schema, and returns the schema to the caller.

Orchestrator (orchestrator.py)
Another A2A server that inspects incoming text:

If it sees “.json” in the text, it forwards the message to the schema agent.

Otherwise, it processes the message via the LLM directly for a regular conversational response.

Sample Data (data/out.json)
A simple example JSON file you can use to test the full pipeline.

Launcher Script (main.py)
An optional convenience script that spawns all three components (MCP server, schema agent, and orchestrator) so you can run them together without needing multiple terminals.

Prerequisites
Python 3.8 or higher

Ollama (or any A2A-compliant LLM backend) running locally on http://localhost:11434.
Make sure you have downloaded at least one model (for example, gemma3:12b).

pip (to install Python packages)

Directory Structure
graphql
Copy
Edit
.
├── agents
│   ├── schema_agent.py       # A2A agent that calls the MCP tool
│   └── schema_tool.py        # FastMCP server exposing the `analyze_schema` tool
│
├── data
│   └── out.json              # Sample JSON input for testing
│
├── main.py                   # (Optional) Launcher to start all components at once
├── orchestrator
│   └── orchestrator.py       # A2A “router” that forwards .json messages to the schema agent
│
├── client_interactive.py     # Simple command-line client to talk to the orchestrator
└── requirements.txt          # Python dependencies
Components
MCP Server (schema_tool.py)
Role: Hosts a single MCP tool named analyze_schema.

Functionality:

Instantiates a FastMCP server with metadata (name, version, description).

Registers the analyze_schema tool, which takes a list of raw JSON strings, sends each one to the LLM with a strict “output only JSON-Schema” prompt, and returns the resulting schema strings.

Builds a FastAPI application via create_fastapi_app(mcp), exposing JSON-RPC endpoints under /a2a (as well as optional REST endpoints under /tools/analyze_schema).

Endpoint:

JSON-RPC is available at /a2a.

The tool can be discovered via a JSON-RPC initialize call and then invoked directly.

Schema Agent (schema_agent.py)
Role: An A2A agent that handles JSON file analysis requests.

Functionality:

Uses an A2A agent card to register itself as “Schema Analyzer Agent.”

Connects to the MCP server’s JSON-RPC endpoint (e.g., http://localhost:8001/a2a).

In its message handler, scans incoming text for substrings ending in .json.

Reads each referenced JSON file from the local data/ directory, collects the raw JSON, and calls the MCP tool (analyze_schema) via call_mcp_tool.

Returns the schema result(s) as a chat response.

Endpoint:

A2A messages are served at /a2a on port 8002.

Orchestrator (orchestrator/orchestrator.py)
Role: Routes messages either to the schema agent or to a regular LLM response.

Functionality:

Inherits from an Ollama-backed A2A server.

In the async message handler, checks if the incoming text contains “.json.”

If it does, forwards the entire message to the schema agent’s A2A endpoint (e.g., http://localhost:8002/a2a) via an A2AClient.

Otherwise, uses super().handle_message(...) to let the LLM respond normally.

Endpoint:

A2A messages are served at /a2a on port 8000.

Sample Data (data/out.json)
Role: Provides a simple JSON file for demonstration.

Content:
A minimal JSON object with a few fields (e.g., numeric, array, nested object) that can be used to test schema generation.

Launcher (main.py)
Role: Convenience script to start all three services in one process or via background subprocesses.

Functionality:

Spawns the MCP server (FastAPI via Uvicorn).

Launches the schema agent as a separate process.

Launches the orchestrator as another process.

Prints logs to the console so you can monitor each component.

Usage: Run python3 main.py to launch MCP ➔ schema agent ➔ orchestrator in sequence.

Installation & Setup
Ensure Ollama is running (with at least one model downloaded).

Install Python dependencies by running:

nginx
Copy
Edit
pip install -r requirements.txt
Verify that you have the following files in place:

agents/schema_tool.py

agents/schema_agent.py

orchestrator/orchestrator.py

data/out.json

main.py (optional)

client_interactive.py

requirements.txt

Running the Pipeline
1. Start Ollama
If Ollama is not already running, launch it with a model (e.g., gemma3:12b) so that the MCP server can call it:

nginx
Copy
Edit
ollama serve gemma3:12b --api-url http://localhost:11434
2. Start the MCP Server
In a terminal, navigate to the repository root and run the MCP server:

nginx
Copy
Edit
uvicorn agents.schema_tool:app --host 0.0.0.0 --port 8001
This starts FastAPI on port 8001.

JSON-RPC endpoint: http://localhost:8001/a2a.

3. Start the Schema Agent
Open a new terminal window and run:

bash
Copy
Edit
python3 agents/schema_agent.py
This starts an A2A server on port 8002.

Endpoint: http://localhost:8002/a2a.

Watches for messages containing .json and invokes the MCP tool.

4. Start the Orchestrator
In another terminal, run:

bash
Copy
Edit
python3 orchestrator/orchestrator.py
This starts an A2A server on port 8000.

Endpoint: http://localhost:8000/a2a.

Forwards “.json” requests to the schema agent; otherwise, replies via the LLM.

5. Use the Interactive Client
Open a fourth terminal and run:

nginx
Copy
Edit
python3 client_interactive.py
You will see a prompt You:.

Type normal chat text (e.g., “Hello!”) to get a conversational response.

To generate a schema, type something like: Analyze out.json

The orchestrator notices “out.json,” forwards to the schema agent.

The schema agent reads data/out.json, calls the MCP tool, and returns a strict JSON-Schema.

6. (Optional) Single-Script Launcher
Instead of manually starting each component, you can run:

css
Copy
Edit
python3 main.py
This will spawn the MCP server, schema agent, and orchestrator in the background.

All logs will appear in that single console.

Example Interaction Flow
User runs client_interactive.py and sees You:.

User types “Please analyze out.json.”

Interactive Client sends an A2A message to the orchestrator at http://localhost:8000/a2a.

Orchestrator detects “.json” and forwards to the schema agent at http://localhost:8002/a2a.

Schema Agent opens data/out.json, reads raw JSON, and calls the MCP tool (analyze_schema) via JSON-RPC to http://localhost:8001/a2a.

MCP Server (via FastAPI) receives the JSON-RPC request, passes the raw JSON to the LLM proxy, and returns a strict draft-07 schema string.

Schema Agent receives the schema(s) from MCP and returns as an A2A response.

Orchestrator relays the response back to the interactive client.

Interactive Client prints the JSON-Schema text for the user.

Customization
Switch between JSON-RPC and REST:

In schema_tool.py, you can choose to expose only REST (/tools/analyze_schema) by adjusting how you mount the FastAPI app.

Update schema_agent.py so that it points to the REST endpoint instead of JSON-RPC.

Modify the LLM prompt:

In schema_tool.py, edit the Ollama system prompt to adjust how the model formats its JSON-Schema (e.g., draft-04 vs. draft-07, add “additionalProperties”: false, etc.).

Add additional MCP tools:

Simply register more functions with @mcp.tool() in schema_tool.py.

Each new tool will automatically appear in the JSON-RPC “initialize” response.

License
This example is provided under the MIT License. Feel free to copy, modify, and distribute.

Happy JSON-Schema generating!

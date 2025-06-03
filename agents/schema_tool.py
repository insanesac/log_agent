from typing import List
from python_a2a.mcp import FastMCP
from python_a2a import OllamaA2AServer, Message, MessageRole, TextContent
from python_a2a import create_fastapi_app
import uvicorn

system_prompt = """You are a JSON schema analyzer expert. You are given
    a complex json string of which you are to infer the schema for further processing.
    The output should be a valid json enclosed as follows;
    ```json
    {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "entries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                "id":         { "type": "string"  },
                "label":      { "type": "string"  },
                "count":      { "type": "integer" },
                "status": {
                    "type": "object",
                    "properties": {
                    "code": { "type": "integer" },
                    "msg":  { "type": "string"  }
                    }
                },
                "metrics": {
                    "type": "object",
                    "properties": {
                    "average": { "type": "number" },
                    "minimum": { "type": "number" },
                    "maximum": { "type": "number" },
                    "ratio":   { "type": "number" }
                    }
                }
                }
            }
            },
            "version": { "type": "integer" }
        },
        "required": ["entries", "version"]
    }
    ```
    Rules to follow:
    1. Output only a valud JSON object. No explanation, no markdown, no comments.
    2. Do not include any extra keys; only output a schema whose top‐level keys are "$schema",
   "type", "properties", and "required" (and nested "properties"/"required" as needed).
    3. If a value is a number without a decimal, use "type":"integer". If it has a decimal,
    use "type":"number". If it’s true/false, use "type":"boolean". Strings→"string".
    Objects→"object" (with nested rules). Arrays→detect homogeneous item type and use
    "items":{"type":"<child-type>"}. If mixed, use "items":{"oneOf":[…]}.
    4. ALWAYS begin the very first character of your response with "{" and end with "}".  
    No leading whitespace, no trailing whitespace, no extra newlines.
    5. If you cannot parse the input as JSON, immediately output:
    { "error": "Invalid JSON: <reason>" }
    (and nothing else).
    6. EXACTLY follow JSON‐Schema draft‐07 syntax.  Do not invent your own keywords.
    """

mcp = FastMCP(
    name="Schema Analyzer MCP",
    version="0.1.0",
    description="Infer JSON schema from strings"
)

# Setup Ollama LLM
ollama = OllamaA2AServer(
    model="gemma3:12b",
    api_url="http://localhost:11434",
    system_prompt=system_prompt,
    temperature=0.1
)

# Register tool
@mcp.tool()
def analyze_schema(json_data: List[str]) -> List[str] | str:
    if not json_data:
        return "error: No JSON input provided."

    results = []
    for text in json_data:
        msg = Message(content=TextContent(text=text), role=MessageRole.USER)
        reply = ollama.handle_message(msg)
        results.append(reply.content)

    return results

# Run the server
if __name__ == "__main__":
    app = create_fastapi_app(mcp)
    uvicorn.run(app, host="0.0.0.0", port=8001)

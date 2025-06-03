from typing import List
from python_a2a.mcp import FastMCP
from python_a2a import OllamaA2AServer, Message, MessageRole, TextContent
from python_a2a import create_fastapi_app
import uvicorn
import logging                                 # 1

# 1. Configure Python logging BEFORE creating FastAPI app
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)                                               
logger = logging.getLogger(__name__)            


system_prompt = """You are a JSON-schema-inference expert.  

When given a JSON string, you must output exactly the JSON Schema (Draft-07) that describes it.  
• Do NOT output any explanation or narrative—only the schema object.  
• The schema must use only these top-level fields: "$schema", "type", "properties", and "required".  
• If a value is an integer, use "type": "integer". If a value is a float, use "type": "number".  
• If a value is true/false, use "type": "boolean". If a value is a string, use "type": "string".  
• For objects, use "type": "object" and include nested "properties"/"required".  
• For arrays, detect homogeneous item types and use "items": {"type": "<child-type>"}.  
  If the array has mixed types, use "items": {"oneOf": [<sub-schema-list>]}.  
• Always begin the very first character of your response with “{” and end with “}”.  
• If the input is not valid JSON, respond exactly with:
  { "error": "Invalid JSON: <reason>" }  
  (and nothing else).
    """

mcp = FastMCP(
    name="Schema Analyzer MCP",
    version="0.1.0",
    description="Infer JSON schema from strings"
)
logger.info("Initialized FastMCP instance 'Schema Analyzer MCP' v0.1.0")  # 10


# Setup Ollama LLM
ollama = OllamaA2AServer(
    model="gemma3:4b",
    api_url="http://localhost:11434",
    system_prompt=system_prompt,
    temperature=0.1
)
logger.info("Configured OllamaA2AServer with model gemma3:12b")  # 11


# Register tool
@mcp.tool()
def analyze_schema(json_data: List[str]) -> List[TextContent] | str:
    logger.info(f"🔧 analyze_schema called with {len(json_data)} document(s)")
    if not json_data:
        logger.warning("analyze_schema: no input provided")
        return "error: No JSON input provided."

    results = []

    msg = Message(content=TextContent(text=json_data[0]), role=MessageRole.USER)
    
    reply = ollama.handle_message(msg)
    results.append(reply.content)

    logger.info("🔚 analyze_schema returning all results")
    return results

# Run the server
if __name__ == "__main__":
    app = create_fastapi_app(mcp)
    logger.info("🚀 Schema Analyzer MCP server is running")
    uvicorn.run(app, host="0.0.0.0", port=8001)
    
    
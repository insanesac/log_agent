import re
import logging
from typing import Dict
from python_a2a import (
    A2AServer,
    Message,
    FastMCPAgent,
    TextContent,
    MessageRole,
    AgentCard
)
import asyncio
from python_a2a import agent, skill, run_server
from schema_tool import mcp
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

class SchemaAnalyzerAgent(A2AServer, FastMCPAgent):
    def __init__(self):
        """
        Initialize the SchemaAnalyzerAgent.
        """
        self.host = "0.0.0.0"
        self.port = 8002

        # Initialize agent card
        agent_card = AgentCard(
            name="Schema Analyzer Agent with Tools",
            description="An agent that infers schema of a json string",
            url=f"http://localhost:{self.port}",
            version="1.0.0"
        )
        mcp_servers = {}
        mcp_servers['schema_analyzer'] = mcp
        logger.info(f"mcp server -------- {mcp_servers}")
        A2AServer.__init__(self, agent_card=agent_card)
        FastMCPAgent.__init__(
            self,
            mcp_servers=mcp_servers
        )
        logger.info(f"✅ SchemaAnalyzerAgent initialized on {self.host}:{self.port}")
        logger.info("🔁 MCP connection set for: schema_analyzer")

    def handle_message(self, message: Message) -> Message:
        logger.info("📥 Received async message")

        if isinstance(message.content, TextContent):
            text_content = message.content.text
            logger.debug(f"📄 Text content: {text_content}")

            json_files = re.findall(r'(\S+\.json)', text_content)
            logger.info(f"📦 Found JSON file references: {json_files}")

            if json_files:
                json_data = []

                for file in json_files:
                    try:
                        logger.info(f"📂 Attempting to open file: {file}")
                        with open(file, 'r') as f:
                            content = f.read()
                            json_data.append(content)
                            logger.debug(f"📑 Content read from {file}: {content[:10]}...")  # Truncated
                    except FileNotFoundError:
                        logger.error(f"❌ File not found: {file}")
                        return Message(
                            content=TextContent(text=f"File {file} not found."),
                            role=MessageRole.AGENT,
                            parent_message_id=message.message_id,
                            conversation_id=message.conversation_id,
                        )

                logger.info("🔧 Sending data to MCP tool: analyze_schema")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                json_schemas = loop.run_until_complete(
                        self.call_mcp_tool(
                            "schema_analyzer",
                            "analyze_schema",
                            json_data=json_data
                    )
                )
                logger.info(f"✅ Received schema analysis response {json_schemas}")

                return Message(
                    content=TextContent(text=f"JSON Schemas: {json_schemas}"),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id,
                )
            else:
                logger.warning("⚠️ No JSON file references found in text.")
                return Message(
                    content=TextContent(text="No JSON files found in the message."),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id,
                )
        else:
            logger.warning("⚠️ Non-text content received.")
            return Message(
                content=TextContent(text="Message content is not text."),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id,
            )

    def run_agent(self):
        """
        Run the SchemaAnalyzerAgent.
        """
        logger.info("🚀 Starting SchemaAnalyzerAgent server...")
        run_server(self, host=self.host, port=self.port)
        logger.info(f"🟢 SchemaAnalyzerAgent is running on http://{self.host}:{self.port}")

if __name__ == "__main__":
    schema_analyzer_agent = SchemaAnalyzerAgent()
    schema_analyzer_agent.run_agent()

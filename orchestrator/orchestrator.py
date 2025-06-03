import logging
from python_a2a import run_server
from python_a2a import OllamaA2AServer, Message, MessageRole, TextContent
from python_a2a import A2AClient
import asyncio
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

class OrchestratorA2AServer(OllamaA2AServer):
    def __init__(self, schema_endpoint):
        super().__init__(
            model="gemma3:12b",
            api_url="http://localhost:11434",
            temperature=0.1,
            system_prompt="You are a helpful assistant.",
        )
        self.host = "0.0.0.0"
        self.port = 8000
        self.schema_analyzer_client = A2AClient(schema_endpoint)
        logger.info(f"✅ OrchestratorA2AServer initialized on {self.host}:{self.port}")
        logger.info(f"🔁 Schema analyzer client set to: {schema_endpoint}")
        
    def handle_message(self, message: Message) -> Message:
        """Handle incoming messages and route them to the appropriate service."""
        logger.info("📩 Received message")

        if isinstance(message.content, TextContent):
            text_content = message.content.text
            logger.debug(f"📄 Message content: {text_content}")

            if ".json" in text_content.lower():
                logger.info("🔎 Detected JSON reference in message. Forwarding to schema analyzer.")

                response = self.schema_analyzer_client.send_message(message)
                logger.info(f"✅ Response received from schema analyzer.{response}")

                return response
            else:
                logger.info("💬 Processing message locally using Ollama.")
                return super().handle_message(message)
        return  Message(
                    content=TextContent(text="Requested file not found."),
                    role=MessageRole.AGENT,
                    parent_message_id=message.message_id,
                    conversation_id=message.conversation_id,
                )    
    
    def run_orchestrator(self):
        """Run the OrchestratorA2AServer and start listening."""
        logger.info("🚀 Starting Orchestrator A2A Server...")
        run_server(self, host=self.host, port=self.port)

if __name__ == "__main__":
    schema_analyzer_endpoint = "http://localhost:8002"
    orchestrator_server = OrchestratorA2AServer(schema_analyzer_endpoint)
    orchestrator_server.run_orchestrator()

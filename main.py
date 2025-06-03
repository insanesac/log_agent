import logging
import time
from python_a2a import A2AClient, Message, MessageRole, TextContent

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def interactivate_client(client: A2AClient):
    """
    Interact with the A2A client to send a message and receive a response,
    logging how long each round‐trip takes.
    """
    logger.info("🟢 Starting interactive JSON Schema Analyzer client.")
    print("\n===== Json Schema Analyzer Assistant =====")
    print("Type 'exit' to quit the client.\n")
    print("Example input: 'Please analyze the schema of the following JSON files: file1.json, file2.json'\n")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                logger.info("🔴 User exited the interactive session.")
                print("Exiting the client.")
                break

            logger.info(f"📨 User input received: {user_input}")
            message = Message(
                content=TextContent(text=user_input),
                role=MessageRole.USER,
            )

            # Start timer
            start = time.monotonic()
            response = client.send_message(message)
            elapsed = time.monotonic() - start

            logger.info("✅ Response received from A2A server.")
            logger.info(f"⏱ Round‐trip time: {elapsed:.2f} seconds")
            logger.debug(f"📩 Full response: {response}")

            if isinstance(response.content, TextContent):
                print(f"Server: {response.content.text}")
            else:
                print(f"Server: Unknown response type – {response.content}")

        except Exception as e:
            logger.exception("❌ An error occurred during interaction.")
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    orchestrator_endpoint = "http://localhost:8000/a2a"
    logger.info(f"🔗 Connecting to orchestrator at {orchestrator_endpoint}")
    client = A2AClient(endpoint_url=orchestrator_endpoint, timeout=120)
    interactivate_client(client)

import logging
from python_a2a import A2AClient, Message, TextContent, MessageRole

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def interactivate_client(client: A2AClient):
    """
    Interact with the A2A client to send a message and receive a response.

    Args:
        client (A2AClient): The A2A client to interact with.
    """
    logger.info("🟢 Starting interactive JSON Schema Analyzer client.")
    print("\n===== Json Schema Analyzer Assistant =====")
    print("Type 'exit' to quit the client.\n")
    print("Example input: 'Please analyze the schema of the following JSON files: file1.json, file2.json'\n")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                logger.info("🔴 User exited the interactive session.")x
                print("Exiting the client.")
                break

            logger.info(f"📨 User input received: {user_input}")

            message = Message(
                content=TextContent(text=user_input),
                role=MessageRole.USER,
            )
            logger.debug(f"📦 Constructed message object: {message}")

            response = client.send_message(message)

            logger.info("✅ Response received from A2A server.")
            logger.debug(f"📩 Full response: {response}")

            print(f"Server: {response}")

        except Exception as e:
            logger.exception("❌ An error occurred during interaction.")
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    orchestrator_endpoint = "http://localhost:8000"  # Replace with your orchestrator endpoint
    logger.info(f"🔗 Connecting to orchestrator at {orchestrator_endpoint}")
    client = A2AClient(orchestrator_endpoint)
    interactivate_client(client)

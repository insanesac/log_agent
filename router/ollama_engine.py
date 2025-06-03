from python_a2a import OllamaA2AClient
from python_a2a import run_server 

client = OllamaA2AClient(
    api_url="http://localhost:11434",
    model="gemma3:12b",
    temperature=0.7,
    system_prompt="You are a helpful assistant.",
)


from langchain_community.llms import Ollama

class Model:
    def __init__(self):
        self.llm = Ollama(
            model="gemma3:12b",
            verbose=True
        )  
import os
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

class Llama:
    # Todo: Create a class with multiple functions for Llama
    def __init__(self):
        self.model_name = 'llama3.1'

        # Start Llama 
        self._call_llama()
    
    def _call_llama(self):
        model = OllamaLLM(model=self.model_name)
        return model

    def in_scope(self):
        # TODO: Implement a function to determine if this question is in scope
        pass
    
    def get_feedback(self):
        # TODO: Get feedback from llama
        pass

    def get_advice(self):
        # TODO: Get advice from llama
        pass
    def answer_query(self):
        # TODO: Get answers for follow ups from llama
        pass



class Chatgpt:
    # Todo: Create a class with multiple functions for ChatGPT
    def __init__(self):
        pass

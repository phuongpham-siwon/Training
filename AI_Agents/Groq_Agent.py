from openai import OpenAI # import OpenAI SDK as a generic client, 
                          # xAI deliberately made their API compatible with OpenAI’s API schema
import os
import httpx
from dotenv import load_dotenv
import json
from numexpr import evaluate as numexpr

load_dotenv()
# class CalculatorTool():
class Agent:
    """xAI Groq Agent"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("XAI_API_KEY"), 
                             base_url="https://api.x.ai/v1",
                             timeout=httpx.Timeout(3600.0),)
        self.model = "groq-4"
        
        self.message_history = [{
            "role": "system",
            "content": "You are Grok, a highly intelligent assistant that reasons step by step."
        }]


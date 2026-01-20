import anthropic
import os
from dotenv import load_dotenv
import json
# from google.colab import userdata

load_dotenv()

print(anthropic.__version__)
# api_key = os.getenv("ANTHROPIC_API_KEY")
# print(f"API Key: {api_key}")

tools = []

from numexpr import evaluate as numexpr
class CalculatorTool():
    """A tool for performing mathematical calculations"""

    def get_schema(self):
        return {
            "name": "calculator",
            "description": "Performs basic mathematical calculations, use also for simple additions",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2+2', '10*5')"
                    }
                },
                "required": ["expression"]
            }
        }

    def execute(self, expression):
        """
        Args:
            expression (str): The mathematical expression to evaluate
        Returns:
            float: The result of the evaluation
        """
        try:
            result = numexpr(expression)
            # Convert numpy ndarray to native Python type
            if hasattr(result, 'item'):
                result = result.item()
            return {"result": result}
        except:
            return {"error": "Invalid mathematical expression"}

calc = CalculatorTool()
tools.append(calc)

class Agent:
    """A simple AI agent that can answer questions"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) # SDK
        self.model = "claude-sonnet-4-20250514"
        self.system_message = "You are a helpful assistant that breaks down problems into steps and solves them systematically."
        self.messages = []  # Initialize an empty list to store messages (short memory)
        self.tools = tools
        self.tool_map = {tool.get_schema()["name"]: tool for tool in tools}
        # print(f"Registered tools: {self.tool_map}")

    def _get_tool_schemas(self): # allows the agent to know what tools are available and how to use them
        """Get tool schemas for all registered tools"""
        return [tool.get_schema() for tool in self.tools]

    def chat(self, message): 
        """Process a user message and return a response"""
        
        self.messages.append({"role": "user", "content": message})  # Append message to (short memory) message list
            
        response = self.client.messages.create( # Send a request
            model=self.model,
            max_tokens=1024, # Limit the response length
            system=self.system_message,
            tools=self._get_tool_schemas() if self.tools else None,
            messages=self.messages,
            temperature=0.1,
        )

        # Append assistant's full response (which may contain text, tool_use blocks, or both)
        self.messages.append({"role": "assistant", "content": response.content})
           
        return response
        
        

def run_agent():
    agent = Agent()
    while True:
        message = input("Your prompt: ")  # Get user input
            
        if message.strip() == "exit":  # Check for exit before sending to Claude
            break
        
        # response context doesn't handle tool use yet, it is a tool use block
        # so we need to manually check for tool use and execute the tool (user)
        # then return the result as text to the model 
        # The user executes the tool and sends the tool result back to the agent in a follow-up message
        i = 0
        max_iter = 5
        while i < max_iter:
            response = agent.chat(message)

            if response.stop_reason == "tool_use":
                tool_results = []
                for content_block in response.content:
                    if content_block.type == "tool_use": # detect tool use that is content block
                        tool_name = content_block.name # Get the tool name
                        tool_input = content_block.input # Get the tool input

                        # print(f"Using tool {tool_name} with input {tool_input}")    
                        
                        # Execute the tool
                        tool = agent.tool_map[tool_name]
                        # print(f"Executing tool: {tool}")
                        tool_result = tool.execute(**tool_input)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": json.dumps(tool_result)
                        })
                        # print(f"Tool result: {tool_result}")
                message = tool_results  
                i += 1  
            else:
                break
        print(response.content[0].text)

    print("Have a great day! Fern")

run_agent()
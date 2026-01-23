from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from numexpr import evaluate as numexpr

load_dotenv()

class CalculatorTool():
    """A tool for performing mathematical calculations"""

    def get_schema(self):
        return {
            "type": "function",
            "name": "calculator",
            "description": "Performs basic mathematical calculations, use also for simple additions",
            "parameters": {
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
tools = [calc]

class Agent:
    """Open AI Agent"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # SDK
        self.model = "gpt-5"
        self.tools = tools
        self.tool_map = {tool.get_schema()["name"]: tool for tool in tools}
        self.system_message = "You are a helpful assistant that breaks down problems into steps and solves them systematically."
        self.message_history = [{"role": "system", "content": self.system_message}]

    def chat(self, user_prompt):
        """Chat with the agent

        Args:
            user_prompt (str): The user's prompt
        Returns:
            str: The agent's response
        """
        # Construct the messages
        self.message_history.append({"role": "user", "content": user_prompt})

        # Call the OpenAI chat completion API
        response = self.client.responses.create(
            model=self.model,
            input=self.message_history,
            max_output_tokens=1024,
            # temperature=0.1,
            # tools=[tool.get_schema() for tool in self.tools],
        )
        # Append the assistant's response to the message history
        self.message_history.append({"role": "assistant", "content": response.output_text})

        return response

def run_agent():
    agent = Agent()
    while True:
        message = input("Your prompt: ")  

        if message.lower() == "exit":
            break
        response = agent.chat(message)

        max_iterations = 5
        for i in range(max_iterations):
            response = agent.chat(message)

            tool_responses = []
            for item in response.output:
                if item.type == "function_call":
                    tool_name = item.name
                    tool_args = item.arguments

                    if tool_name in agent.tool_map:
                        tool = agent.tool_map[tool_name]
                        tool_response = tool.execute(json.loads(item.arguments))

                        tool_responses.append({
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps(tool_response)
                        })
                    message = tool_responses
                else:
                    break

        print("Agent:", response.output_text)

    print("Bye Fern!")

run_agent()
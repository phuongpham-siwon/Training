from json import tool
from openai import OpenAI # import OpenAI SDK as a generic client
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
            "description": "Performs basic and complex mathematical calculations, use also for simple additions",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2+2', '10*5', '23x123')"
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
        # try:
        #     result = eval(expression)
        #     return {"result": result}
        # except:
        #     return {"error": "Invalid mathematical expression"}

calc = CalculatorTool()
tools = [calc]

class Agent:
    """Open AI Agent"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # SDK
        self.model = "gpt-5"
        self.tools = tools
        self.tool_map = {tool.get_schema()["name"]: tool for tool in tools} # {"calculator": self.calc}
        self.system_message = "You are a helpful assistant that evaluate mathematical expressions using the provided calculator tool."
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
            tools=[tool.get_schema() for tool in self.tools],
            tool_choice = "auto",
            # reasoning={"effort": "minimal"}
        )
        # Append the assistant's response to the message history

        return response

def run_agent():
    agent = Agent()
    while True:
        message = input("Your prompt: ")  

        if message.lower() == "exit":
            break
        # response = agent.chat(message)

        
        response = agent.chat(message)
        for item in response.output:    
            print(item)
            if item.type == "function_call":
                tool_name = item.name

                print(tool_name, agent.tool_map[tool_name])
                if tool_name in agent.tool_map:
                    tool = agent.tool_map[tool_name]
                    tool_response = tool.execute(**json.loads(item.arguments))

                # message = tool_responses
                response = agent.client.responses.create(
                    model=agent.model,
                    input=[
                        {"role": "system", "content": agent.system_message},
                        {"role": "user", "content": message},
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps(tool_response),
                        },
                    ],
                    max_output_tokens=1024,
                )       

            else:
                break
        agent.message_history.append({"role": "assistant", "content": response.output_text})
    
        print("Agent:", response.output_text)

    print("Bye Fern!")

if __name__ == "__main__":
    run_agent()
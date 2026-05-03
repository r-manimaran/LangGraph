import math
import operator
import os
import argparse
import json

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from langchain_aws import ChatBedrock

# For Bedrock Agent core Deployment
# ---------------------------------
app = BedrockAgentCoreApp()



# ---------
# Define the Tools
# ---------

@tool
def calculator(expression: str) -> str:
    """
     Calculate the result of a mathematical expression.
    
     Args:
        expression: A mathematical expression as a string (e.g., "2 + 3 * 4", "sqrt(16)", "sin(pi/2)")
    
     Returns:
        The result of the calculation as a string
     """
    # Implementation here
    try:
        # Define safe functions that can be used in expressions
        safe_dict = {
            "__builtins__": {},
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow,
            # Math functions
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "log": math.log, "log10": math.log10, "exp": math.exp,
            "pi": math.pi, "e": math.e,
            "ceil": math.ceil, "floor": math.floor,
            "degrees": math.degrees, "radians": math.radians,
            # Basic operators (for explicit use)
            "add": operator.add, "sub": operator.sub,
            "mul": operator.mul, "truediv": operator.truediv,
        }
        
        # Evaluate the expression safely
        result = eval(expression, safe_dict)
        return str(result)
    except ZeroDivisionError:
        return "Error: Division by zero"
    except ValueError as e:
        return f"Error: Invalid value - {str(e)}"
    except SyntaxError:
        return "Error: Invalid mathematical expression"
    except Exception as e:
        return f"Error: {str(e)}"
    
# create a custom weather Tool
@tool
def weather()->str:
    """Get the current weather"""
    return "The weather is sunny with a temperature of 25 degrees Celsius."

# ==============
# Agent
# ==============

def create_agent():
    os.environ["AWS_DEFAULT_REGION"]="us-east-1"

    llm= ChatBedrock(
        model_id ="arn:aws:bedrock:us-east-1:395109667422:application-inference-profile/ptbzu6tpt21o",
        provider="anthropic",
        region_name="us-east-1",
        model_kwargs={"temperature":0.1},
    )

    tools = [calculator, weather]
    llm_with_tools = llm.bind_tools(tools)

    system_message = SystemMessage(
        content="You are a helpful assistant. You can do math and provide weather info."
    )

    def chatbot(state: MessagesState):
        messages = state["messages"]

        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [system_message] + messages

        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)

    builder.add_node("chatbot", chatbot)
    builder.add_node("tools",ToolNode(tools))

    builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    builder.add_edge("tools", "chatbot")
    builder.set_entry_point("chatbot")
    
    return builder.compile()

# Initialize the agent
# --------------------
agent = create_agent()

# Set the entry point
@app.entrypoint
def langgraph_bedrock(payload):
    """
    Args:
        payload (dict): The input payload containing the user's message.

    Returns:
        dict: The response from the agent.
    """

    # Extract the user's message from the payload
    user_message = payload.get("prompt", "").strip()

    if not user_message:
        return {"response": "Please provide a non-empty message."}

    # Run the agent with the user's message
    result = agent.invoke({"messages": [HumanMessage(content=user_message)]})

    # Return the final response
    return {"response": result["messages"][-1].content}

if __name__ == "__main__":
   app.run()





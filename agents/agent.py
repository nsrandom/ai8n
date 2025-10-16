from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool, BaseTool, ToolContext
from google.adk.agents.callback_context import CallbackContext

import json
import sys
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Add the parent directory to the path so we can import from the root package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_NAME = "gemini-2.5-flash"

# Load .env file from the parent directory
dotenv_path=f"{os.path.dirname(os.path.abspath(__file__))}/../.env"
print(f"agent.py: Loading .env file from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)

def before_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: CallbackContext):
    print(f"[[Before Tool]] '{tool.name}' with arguments: {args}")
    return None

def after_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict[str, Any]
) -> Optional[Dict]:
    print(f"[[After Tool]] '{tool.name}' with arguments: {args}")
    return None

math_problem_agent = LlmAgent(
    model=MODEL_NAME,
    name="math_problem_agent",
    description="Creates math problems",
    instruction="""
You are a math problem agent that generates a random linear algebra problem.
Create two equations with two variables (x and y) that are linearly independent.
Return the equations as list of strings in JSON format. Example:
```json
{
  "equations": [
    "2x + 3y = 10",
    "4x + 5y = 12"
  ],
  "variables": ["x", "y"]
}
```
""")

linear_algebra_solver_agent = LlmAgent(
    model=MODEL_NAME,
    name="linear_algebra_solver_agent",
    description="Solves linear algebra problems",
    instruction="""
You are a linear algebra solver agent that solves linear algebra problems.
You will be given a list of equations in JSON format.
Solve the equations and return the solution as a JSON object. 
If there is an error, return the error in the error field.
Example output:
```json
{
  "solution": {
    "x": 1,
    "y": 2
  },
  "error": null,
}
```
""")

# Create the math agent
math_agent = LlmAgent(
    model=MODEL_NAME,
    name="math_agent",
    description="Creates and solves math problems",
    instruction="""
You are a math agent that creates and solves math problems.

**Tasks**
1. Create a math problem using the `create_math_problem_tool`.
2. Solve the math problem using the `solve_math_problem_tool`.
4. Provide a summary of what was accomplished.
""",
    tools=[
        AgentTool(math_problem_agent),
        AgentTool(linear_algebra_solver_agent),
    ],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)


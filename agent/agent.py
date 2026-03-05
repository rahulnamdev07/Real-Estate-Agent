
# agent.py

import asyncio
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient

from langgraph.graph import StateGraph
from langgraph.actions.tool import ToolAction

async def main():
    os.environ["GOOGLE_API_KEY"] = "AIzaSyA90bAktAuEk37am9sRe_gYHxu3_7tjb3Y"

    # Connect to MCP server
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["mcp_server.py"],
                "transport": "stdio",
            }
        }
    )
    tools = await client.get_tools()

    # LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
    )

    # Build a simple StateGraph for ReAct
    graph = StateGraph(llm=llm)

    # Add MCP tools to graph
    for tool in tools:
        graph.add_action(ToolAction(tool))

    # Run the agent
    response = await graph.run("What is 25 + 17?")

    print("\nFinal Response:\n", response)


if __name__ == "__main__":
    asyncio.run(main())
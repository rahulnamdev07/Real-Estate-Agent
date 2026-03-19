import asyncio
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent


load_dotenv()


async def main():
    # 1. Load API Key
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

    # 2. Initialize MCP Client
    client = MultiServerMCPClient(
        {
            "real_estate": {
                "command": "python",
                "args": ["server.py"],
                "transport": "stdio",
            }
        }
    )

    try:
        # 3. Fetch Tools from MCP Server
        tools = await client.get_tools()
        print(f"✅ Connected. Tools found: {[t.name for t in tools]}")

        # 4. Initialize LLM (Gemini)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
        )

        # 5. Create Agent (New API - replaces create_react_agent)
        agent = create_agent(
            model=llm,
            tools=tools,
        )

        # 6. Query
        query = "Get real estate stats and neighborhood insights for MP Nagar, Bhopal."

        # 7. Invoke Agent
        response = await agent.ainvoke(
            {
                "messages": [
                    {"role": "user", "content": query}
                ]
            }
        )

        # 8. Print Final Output
        print("\n--- 🤖 Agent Response ---\n")
        print(response["messages"][-1].content)

    except Exception as e:
        print("❌ Error occurred:", str(e))


if __name__ == "__main__":
    asyncio.run(main())
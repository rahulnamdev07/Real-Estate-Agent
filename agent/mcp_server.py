# mcp_server.py

from mcp.server.fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("SimpleMathServer")


@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """
    Add two numbers and return the result.
    """
    return a + b


if __name__ == "__main__":
    # Run the MCP server over stdio transport
    mcp.run(transport="stdio")
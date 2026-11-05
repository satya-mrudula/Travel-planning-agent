from mcp.server.fastmcp import FastMCP
from urllib.parse import quote
import json

mcp = FastMCP("MapsMCPServer")

@mcp.tool()
def create_route(origin: str, destination: str) -> str:
    """Create route links using public map services; does not return live navigation."""
    return json.dumps({
        "origin": origin,
        "destination": destination,
        "openstreetmap": f"https://www.openstreetmap.org/directions?from={quote(origin)}&to={quote(destination)}",
        "google_maps": f"https://www.google.com/maps/dir/{quote(origin)}/{quote(destination)}"
    })

if __name__ == "__main__":
    mcp.run(transport="stdio")

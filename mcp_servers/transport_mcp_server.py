from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("TransportMCPServer")

@mcp.tool()
def find_transport(origin: str, destination: str, preferred_mode: str = "any") -> str:
    """Suggest intercity and local transport types; fares and schedules are not live."""
    return json.dumps({
        "journey": {"origin": origin, "destination": destination},
        "preferred_mode": preferred_mode,
        "intercity_options": [
            {"mode": "Train", "description": "Often economical for families; check IRCTC for current fare and availability."},
            {"mode": "Bus", "description": "Budget-friendly option; check operator websites for current schedules and fares."},
            {"mode": "Flight", "description": "Faster but generally costlier; check airline websites for current fares."}
        ],
        "local_options": [
            {"mode": "Metro", "description": "Affordable for connected city routes."},
            {"mode": "City bus", "description": "Low-cost local travel."},
            {"mode": "Auto/cab", "description": "Useful for short trips or family convenience."}
        ],
        "live_booking": False
    })

if __name__ == "__main__":
    mcp.run(transport="stdio")

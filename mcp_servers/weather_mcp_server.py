from mcp.server.fastmcp import FastMCP
import json
import requests

mcp = FastMCP("WeatherMCPServer")

@mcp.tool()
def get_weather(city: str) -> str:
    """Fetch a basic current weather snapshot using free Open-Meteo endpoints."""
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=12
        )
        geo.raise_for_status()
        places = geo.json().get("results", [])
        if not places:
            return json.dumps({"available": False, "message": "City not found by weather service."})
        place = places[0]
        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": place["latitude"], "longitude": place["longitude"],
                    "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code",
                    "timezone": "auto"},
            timeout=12
        )
        weather.raise_for_status()
        return json.dumps({"available": True, "city": place["name"], "current": weather.json().get("current", {}),
                           "note": "Current snapshot only; check the forecast again close to travel dates."})
    except Exception as exc:
        return json.dumps({"available": False, "message": str(exc), "note": "Weather lookup failed; continue without weather data."})

if __name__ == "__main__":
    mcp.run(transport="stdio")

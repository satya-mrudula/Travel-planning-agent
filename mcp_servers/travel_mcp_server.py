
from mcp.server.fastmcp import FastMCP
import requests
import json
import time

mcp = FastMCP("TravelMCPServer")

HEADERS = {
    "User-Agent": "TravelPlanningMAS/1.0 (educational project)"
}

city_cache = {}


@mcp.tool()
def search_destinations(city: str) -> str:
    """Find tourist attractions in a city using OpenStreetMap."""

    try:
        key = city.lower().strip()

        if key not in city_cache:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": city,
                    "format": "json",
                    "limit": 1
                },
                headers=HEADERS,
                timeout=15
            )

            response.raise_for_status()
            results = response.json()

            if not results:
                return json.dumps([])

            latitude = float(results[0]["lat"])
            longitude = float(results[0]["lon"])

            city_cache[key] = (latitude, longitude)

            # Respect Nominatim's public usage policy.
            time.sleep(1.1)

        else:
            latitude, longitude = city_cache[key]

        query = f"""
        [out:json][timeout:25];
        (
          nwr(around:12000,{latitude},{longitude})
          ["name"]["tourism"~"attraction|museum|viewpoint|zoo|theme_park"];

          nwr(around:12000,{latitude},{longitude})
          ["name"]["historic"];

          nwr(around:12000,{latitude},{longitude})
          ["name"]["leisure"="park"];
        );
        out center tags 30;
        """

        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            headers=HEADERS,
            timeout=45
        )

        response.raise_for_status()
        data = response.json()

        attractions = []
        seen = set()

        for place in data.get("elements", []):
            tags = place.get("tags", {})
            name = tags.get("name")

            if not name or name.lower() in seen:
                continue

            seen.add(name.lower())

            attractions.append({
                "name": name,
                "category": (
                    tags.get("tourism")
                    or tags.get("historic")
                    or tags.get("leisure")
                    or "Attraction"
                )
            })

            if len(attractions) >= 15:
                break

        return json.dumps(attractions)

    except Exception as error:
        return json.dumps({
            "error": str(error)
        })


@mcp.tool()
def suggest_transport(origin: str = "", destination: str = "", preferred_mode: str = "any") -> str:
    """Suggest intercity and local transport options; prices and schedules are not live."""

    options = [
        {
            "mode": "Metro",
            "description": "Affordable urban transportation"
        },
        {
            "mode": "Bus",
            "description": "Economical public transportation"
        },
        {
            "mode": "Auto",
            "description": "Suitable for short-distance travel"
        },
        {
            "mode": "Cab",
            "description": "Convenient for families and groups"
        },
        {
            "mode": "Rental vehicle",
            "description": "Flexible travel between attractions"
        }
    ]

    result = {
        "journey": {"origin": origin, "destination": destination},
        "preferred_mode": preferred_mode,
        "intercity_options": [
            {"mode": "Train", "description": "Usually economical for intercity family travel; check IRCTC for current fares and availability."},
            {"mode": "Bus", "description": "Budget option; check operator websites for current schedules and fares."},
            {"mode": "Flight", "description": "Faster but often more expensive; check airline websites for current fares."}
        ],
        "local_options": options
    }
    return json.dumps(result)


@mcp.tool()
def get_map_links(origin: str, destination: str) -> str:
    """Create public OpenStreetMap and Google Maps route links for the journey."""
    from urllib.parse import quote
    origin_q = quote(origin)
    destination_q = quote(destination)
    return json.dumps({
        "openstreetmap_route": f"https://www.openstreetmap.org/directions?from={origin_q}&to={destination_q}",
        "google_maps_route": f"https://www.google.com/maps/dir/{origin_q}/{destination_q}"
    })


if __name__ == "__main__":
    mcp.run(transport="stdio")

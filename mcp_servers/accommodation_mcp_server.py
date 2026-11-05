from mcp.server.fastmcp import FastMCP
import requests
import json
import time

mcp = FastMCP("AccommodationMCPServer")

HEADERS = {
    "User-Agent": "TravelPlanningMAS/2.0 EducationalProject"
}

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter"
]

RATES = {
    "budget": 1200,
    "standard": 2500,
    "premium": 4500
}


def get_coordinates(city):
    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "q": city,
            "format": "json",
            "limit": 1
        },
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()
    results = response.json()

    if not results:
        raise ValueError(f"City not found: {city}")

    return float(results[0]["lat"]), float(results[0]["lon"])


def search_overpass(query):
    for server in OVERPASS_SERVERS:
        for attempt in range(2):
            try:
                response = requests.post(
                    server,
                    data={"data": query},
                    headers=HEADERS,
                    timeout=45
                )

                if response.status_code in (429, 502, 503, 504):
                    if attempt == 0:
                        time.sleep(3)
                        continue
                    break

                response.raise_for_status()
                return response.json()

            except requests.RequestException as error:
                print(f"Overpass error: {error}")

                if attempt == 0:
                    time.sleep(2)

    return None


@mcp.tool()
def suggest_accommodation(city: str, preference: str = "budget") -> str:
    """
    Find mapped hotels, hostels and guest houses.
    Provides estimated accommodation costs if the map service is unavailable.
    """

    preference = preference.lower().strip()

    if preference not in RATES:
        preference = "budget"

    estimated_rate = RATES[preference]

    hotels = []
    source = "Estimated fallback"

    try:
        latitude, longitude = get_coordinates(city)

        query = f"""
        [out:json][timeout:30];
        (
          nwr(around:15000,{latitude},{longitude})
          ["tourism"~"hotel|hostel|guest_house"];

          nwr(around:15000,{latitude},{longitude})
          ["building"="hotel"];
        );
        out center tags 40;
        """

        data = search_overpass(query)

        if data:
            seen = set()

            for place in data.get("elements", []):
                tags = place.get("tags", {})
                name = tags.get("name")

                if not name:
                    continue

                if name.lower() in seen:
                    continue

                seen.add(name.lower())

                address_parts = [
                    tags.get("addr:street"),
                    tags.get("addr:suburb"),
                    tags.get("addr:city")
                ]

                address = ", ".join(
                    part for part in address_parts if part
                )

                map_url = (
                    "https://www.google.com/maps/search/?api=1&query="
                    + requests.utils.quote(name + " " + city)
                )

                hotels.append({
                    "name": name,
                    "type": tags.get("tourism", "Hotel"),
                    "address": address or "Address not available",
                    "map_url": map_url
                })

            if hotels:
                source = "OpenStreetMap"

    except Exception as error:
        print("Accommodation search failed:", error)

    if hotels:
        status = "Mapped accommodation listings retrieved"
    else:
        status = "Hotel lookup unavailable; estimated options provided"

        hotels = [
            {
                "category": "Budget hotel",
                "estimated_nightly_cost": 1200,
                "description": "Basic rooms and essential facilities"
            },
            {
                "category": "Budget family stay",
                "estimated_nightly_cost": 1800,
                "description": "Affordable accommodation for families"
            },
            {
                "category": "Standard family hotel",
                "estimated_nightly_cost": 2500,
                "description": "Comfortable rooms and additional facilities"
            },
            {
                "category": "Premium hotel",
                "estimated_nightly_cost": 4500,
                "description": "Higher-end rooms and facilities"
            }
        ]

    result = {
        "city": city,
        "preference": preference,
        "source": source,
        "status": status,
        "hotels": hotels,
        "estimated_nightly_budget_inr": estimated_rate,
        "notice": (
            "Mapped listings are not confirmed booking availability. "
            "Nightly costs are estimates, not live hotel quotations. "
            "Check the hotel directly before booking."
        )
    }

    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
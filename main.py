import asyncio
import json
import sys

from pathlib import Path
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agents.requirement_agent import requirement_agent
from agents.destination_agent import destination_agent
from agents.accommodation_agent import accommodation_agent
from agents.transportation_agent import transportation_agent
from agents.budget_agent import budget_agent
from agents.itinerary_agent import itinerary_agent


BASE_DIR = Path(__file__).resolve().parent


async def start_mcp_server(stack, server_file):
    server_path = BASE_DIR / "mcp_servers" / server_file

    parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)]
    )

    read_stream, write_stream = await stack.enter_async_context(
        stdio_client(parameters)
    )

    session = await stack.enter_async_context(
        ClientSession(read_stream, write_stream)
    )

    await session.initialize()
    print(f"{server_file} connected successfully!")

    return session


async def call_mcp_tool(session, tool_name, arguments, fallback=None, retries=1):
    last_error = None

    for attempt in range(retries + 1):
        try:
            result = await session.call_tool(tool_name, arguments)

            if result.isError:
                raise RuntimeError(f"MCP tool failed: {tool_name}")

            for item in result.content:
                if hasattr(item, "text"):
                    return json.loads(item.text)

            raise RuntimeError(f"No response received from {tool_name}")

        except Exception as error:
            last_error = error
            print(
                f"Retrying {tool_name}: "
                f"attempt {attempt + 1} failed - {error}"
            )

    if fallback is not None:
        print(f"Using fallback information for {tool_name}.")
        return fallback

    raise RuntimeError(
        f"{tool_name} failed after retries: {last_error}"
    )


async def main():
    print("\n" + "=" * 60)
    print("          MULTI-AGENT TRAVEL PLANNING SYSTEM")
    print("=" * 60)

    requirements = requirement_agent()

    async with AsyncExitStack() as stack:

        print("\n========== CONNECTING MCP SERVERS ==========")

        travel_session = await start_mcp_server(
            stack, "travel_mcp_server.py"
        )

        accommodation_session = await start_mcp_server(
            stack, "accommodation_mcp_server.py"
        )

        weather_session = await start_mcp_server(
            stack, "weather_mcp_server.py"
        )

        maps_session = await start_mcp_server(
            stack, "maps_mcp_server.py"
        )

        transport_session = await start_mcp_server(
            stack, "transport_mcp_server.py"
        )

        print("\n========== DESTINATION SEARCH ==========")

        attractions = await call_mcp_tool(
            travel_session,
            "search_destinations",
            {"city": requirements["destination"]},
            fallback=[]
        )

        if isinstance(attractions, dict):
            attractions = []

        if not attractions:
            attractions = [{
                "name": "No mapped attractions found",
                "category": "Unavailable"
            }]

        destination_result = destination_agent(
            requirements,
            attractions
        )

        print("\n========== ACCOMMODATION SEARCH ==========")

        accommodation_options = await call_mcp_tool(
            accommodation_session,
            "suggest_accommodation",
            {
                "city": requirements["destination"],
                "preference": requirements["accommodation"]
            },
            fallback={
                "city": requirements["destination"],
                "preference": requirements["accommodation"],
                "hotels": [],
                "estimated_nightly_budget_inr": 1200,
                "status": "Accommodation search unavailable"
            }
        )

        print(json.dumps(accommodation_options, indent=2))

        accommodation_result = accommodation_agent(
            requirements,
            accommodation_options
        )

        print("\n========== TRANSPORTATION SEARCH ==========")

        transport_options = await call_mcp_tool(
            transport_session,
            "find_transport",
            {
                "origin": requirements["origin"],
                "destination": requirements["destination"],
                "preferred_mode": requirements["transport"]
            },
            fallback={
                "journey": {
                    "origin": requirements["origin"],
                    "destination": requirements["destination"]
                },
                "intercity_options": [],
                "local_options": [],
                "live_booking": False
            }
        )

        print(json.dumps(transport_options, indent=2))

        print("\n========== FLIGHT SEARCH ==========")

        flight_options = await call_mcp_tool(
            transport_session,
            "search_flights",
            {
                "origin": requirements["origin"],
                "destination": requirements["destination"]
            },
            fallback={
                "origin": requirements["origin"],
                "destination": requirements["destination"],
                "airlines_to_check": [
                    "IndiGo",
                    "Air India",
                    "Air India Express",
                    "Akasa Air",
                    "SpiceJet"
                ],
                "availability": "Check booking websites"
            }
        )

        print("\nFlight options:")
        print(json.dumps(flight_options, indent=2))

        print("\n========== MAPS ==========")

        map_result = await call_mcp_tool(
            maps_session,
            "create_route",
            {
                "origin": requirements["origin"],
                "destination": requirements["destination"]
            },
            fallback={
                "message": "Map service unavailable."
            }
        )

        print(json.dumps(map_result, indent=2))

        print("\n========== WEATHER ==========")

        weather_result = await call_mcp_tool(
            weather_session,
            "get_weather",
            {"city": requirements["destination"]},
            fallback={
                "available": False,
                "message": "Weather service unavailable."
            }
        )

        print(json.dumps(weather_result, indent=2))

        print("\n========== TRANSPORTATION AGENT ==========")

        transportation_result = transportation_agent(
            requirements,
            {
                "transport_options": transport_options,
                "flight_options": flight_options
            }
        )

        print("\n========== BUDGET AGENT ==========")

        hotel_cost = accommodation_options.get(
            "estimated_nightly_budget_inr",
            1200
        )

        try:
            hotel_cost = float(hotel_cost)
        except (ValueError, TypeError):
            hotel_cost = 1200

        budget_result = budget_agent(
            requirements,
            hotel_cost
        )

        print("\n========== ITINERARY AGENT ==========")

        travel_context = {
            "maps": map_result,
            "weather": weather_result,
            "accommodation": accommodation_options,
            "transport": transport_options,
            "flights": flight_options
        }

        final_itinerary = itinerary_agent(
            requirements,
            destination_result,
            accommodation_result,
            transportation_result,
            budget_result,
            travel_context
        )

        print("\n" + "=" * 60)
        print("          TRAVEL PLANNING COMPLETED")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
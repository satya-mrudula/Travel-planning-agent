# Travel Planning MAS – MCP setup and test notes

## No paid LLM/API required
- All six agents continue to use the local Ollama model `llama3.2`.
- MCP servers run locally over stdio using the Python MCP SDK.
- Destination data uses public OpenStreetMap/Nominatim/Overpass services.
- Maps MCP creates public map-route links.
- Transport MCP suggests train, bus, flight and local transport categories; it does not fetch live schedules/fares.
- Weather uses the free Open-Meteo endpoints.
- Hotel MCP searches named hotel/hostel place records from OpenStreetMap and returns estimated accommodation categories/rates separately. It does not provide live prices or availability.
- Transport choices are suggestions, not live fares, schedules or ticket availability.

## Run
1. Start Ollama in a terminal: `ollama serve` (if it is not already running).
2. Ensure model exists: `ollama pull llama3.2`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run from this folder: `python main.py`.

The Requirement Agent now asks for origin city before destination city. MCP calls retry once; if still unavailable, the program uses clearly labelled fallback information for optional lookups.

## Test cases
Run: `python -m unittest discover -s tests -v`

Expected: 2 PASS cases and 2 intentional FAIL-input cases caught by validation (the test suite itself should report 4 tests OK).

| Case | Input | Expected result |
|---|---|---|
| TC01 | Valid origin/destination, 3 days, 4 travelers, positive budget | PASS – requirements accepted |
| TC02 | Valid trip details and hotel estimate | PASS – budget calculated |
| TC03 | Days = 0 | FAIL – rejected with validation message |
| TC04 | Budget = -5000 | FAIL – rejected with validation message |

## Refinement / recovery method
1. Validate user inputs before agent execution; ask the user to correct missing city, zero/negative days, travelers or budget.
2. If an MCP request fails, retry it once.
3. If it still fails, use the configured fallback for non-critical data and label it as an estimate/unavailable. Do not invent live prices or bookings.
4. If Ollama is unavailable, start `ollama serve`, confirm `ollama list`, and rerun the application.
5. Re-run all four tests after changing an agent or MCP server.

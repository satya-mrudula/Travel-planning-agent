
import ollama

MODEL = "llama3.2"


def itinerary_agent(requirements, destinations, accommodation,
                    transportation, budget, travel_context=None):
    print("\n========== ITINERARY AGENT ==========")

    prompt = f"""
You are the final Itinerary Agent in a Multi-Agent Travel Planning System.

Create a personalized travel itinerary using the information from the
other specialized agents.

USER REQUIREMENTS:
{requirements}

DESTINATION AGENT RECOMMENDATIONS:
{destinations}

ACCOMMODATION AGENT RECOMMENDATIONS:
{accommodation}

TRANSPORTATION AGENT RECOMMENDATIONS:
{transportation}

BUDGET AGENT CALCULATIONS:
{budget}

Instructions:
1. Create a day-wise itinerary for exactly {requirements['days']} days.
2. Organize activities into morning, afternoon and evening.
3. Use the attractions recommended by the Destination Agent.
4. Include accommodation and transportation suggestions.
5. Include the complete expense breakdown.
6. State whether the estimated trip is within the user's budget.
7. Do not invent hotel bookings, transport schedules or confirmed prices.
8. If the estimated cost exceeds the budget, suggest ways to reduce expenses.
9. Make the plan suitable for {requirements['people']} travelers.

Use clear headings and a professional format.
"""

    prompt += f"\nMAPS AND WEATHER MCP RESULTS:\n{travel_context or {}}\n"

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.message.content

    print("\n========== FINAL TRAVEL ITINERARY ==========\n")
    print(result)

    return result

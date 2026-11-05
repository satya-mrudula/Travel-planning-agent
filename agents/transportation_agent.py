
import ollama

MODEL = "llama3.2"


def transportation_agent(requirements, transport_options):
    print("\n========== TRANSPORTATION AGENT ==========")

    prompt = f"""
You are the Transportation Agent in a travel planning MAS.

Origin: {requirements['origin']}
Destination: {requirements['destination']}
Travelers: {requirements['people']}
Duration: {requirements['days']} days
Budget: Rs. {requirements['budget']}
Preferred transport: {requirements['transport']}

Available transportation options:
{transport_options}

Tasks:
1. Recommend suitable transportation options.
2. Consider affordability and family convenience.
3. Explain when each transport option is useful.
4. Respect the user's preferred transport where possible.
5. Do not invent live schedules, ticket prices or availability.

Return a practical transportation recommendation.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.message.content
    print(result)
    return result

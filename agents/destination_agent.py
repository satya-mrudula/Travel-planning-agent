
import ollama

MODEL = "llama3.2"


def destination_agent(requirements, attractions):
    print("\n========== DESTINATION AGENT ==========")

    prompt = f"""
You are the Destination Agent in a multi-agent travel planning system.

Destination: {requirements['destination']}
Travel duration: {requirements['days']} days
Travelers: {requirements['people']}
Preferences: {requirements['preferences']}

Attractions retrieved from OpenStreetMap:
{attractions}

Tasks:
1. Select relevant attractions based on the user's preferences.
2. Prioritize popular and varied sightseeing options.
3. Organize attractions across the available days.
4. Do not invent attractions that are not in the supplied data.
5. Mention that the attraction data comes from OpenStreetMap.

Return a clear list of recommended attractions with short descriptions.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.message.content
    print(result)
    return result

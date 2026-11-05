
import ollama

MODEL = "llama3.2"


def accommodation_agent(requirements, accommodation_options):
    print("\n========== ACCOMMODATION AGENT ==========")

    prompt = f"""
You are the Accommodation Agent in a travel planning MAS.

Destination: {requirements['destination']}
Number of travelers: {requirements['people']}
Duration: {requirements['days']} days
Total trip budget: Rs. {requirements['budget']}
Accommodation preference: {requirements['accommodation']}

Available accommodation options:
{accommodation_options}

Tasks:
1. Recommend the most suitable accommodation option.
2. Consider the user's budget and preference.
3. Explain the estimated nightly cost.
4. Calculate the approximate total accommodation cost.
5. Do not claim that any hotel is actually booked or has live availability.
6. Clearly identify these as estimated accommodation options.

Return a concise recommendation.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.message.content
    print(result)
    return result

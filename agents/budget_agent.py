def budget_agent(requirements, hotel_cost_per_night):
    print("\n========== BUDGET AGENT ==========")

    days = requirements["days"]
    people = requirements["people"]
    budget = requirements["budget"]
    mode = requirements.get("transport", "any").lower()

    accommodation = hotel_cost_per_night * max(days - 1, 1)
    food = 500 * people * days
    local_transport = 500 * days
    sightseeing = 250 * people

    # Planning estimates only; these are not live ticket quotations.
    if requirements.get("origin", "").strip().lower() == requirements["destination"].strip().lower():
        intercity_transport = 0
    elif mode == "flight":
        intercity_transport = 4500 * people
    elif mode in ("train", "bus"):
        intercity_transport = 1500 * people
    else:
        intercity_transport = 2000 * people

    total = accommodation + food + local_transport + sightseeing + intercity_transport
    remaining = budget - total

    result = {
        "Origin-to-destination transport (estimate)": intercity_transport,
        "Accommodation": accommodation,
        "Food": food,
        "Local transport": local_transport,
        "Sightseeing": sightseeing,
        "Total Estimated Cost": total,
        "Total Budget": budget,
        "Remaining Budget": remaining,
        "Within Budget": total <= budget
    }

    print("\nEstimated Expense Breakdown:")
    for category, amount in result.items():
        if isinstance(amount, bool):
            print(f"{category}: {amount}")
        elif isinstance(amount, (int, float)):
            print(f"{category}: Rs. {amount:,.2f}")
        else:
            print(f"{category}: {amount}")

    return result

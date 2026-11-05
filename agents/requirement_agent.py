
def requirement_agent():
    print("\n========== REQUIREMENT AGENT ==========")

    origin = input("Enter your origin city: ").strip()

    while not origin:
        origin = input("Please enter your origin city: ").strip()

    destination = input("Enter destination city: ").strip()

    while not destination:
        destination = input("Please enter a destination: ").strip()

    while True:
        try:
            days = int(input("Number of travel days: "))
            if days > 0:
                break
            print("Days must be greater than zero.")
        except ValueError:
            print("Enter a valid number.")

    while True:
        try:
            people = int(input("Number of travelers: "))
            if people > 0:
                break
            print("Travelers must be greater than zero.")
        except ValueError:
            print("Enter a valid number.")

    while True:
        try:
            budget = float(input("Total budget (INR): "))
            if budget > 0:
                break
            print("Budget must be greater than zero.")
        except ValueError:
            print("Enter a valid amount.")

    preferences = input(
        "Travel preferences (adventure, history, nature, shopping, etc.): "
    ).strip()

    accommodation = input(
        "Accommodation preference (budget, standard, premium): "
    ).strip().lower()

    transport = input(
        "Preferred transport (bus, train, flight, cab, any): "
    ).strip().lower()

    requirements = {
        "origin": origin,
        "destination": destination,
        "days": days,
        "people": people,
        "budget": budget,
        "preferences": preferences or "General sightseeing",
        "accommodation": accommodation or "budget",
        "transport": transport or "any"
    }

    print("\nRequirements collected successfully!")

    return requirements

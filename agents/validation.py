def validate_requirements(requirements):
    required_text = ("origin", "destination")
    for field in required_text:
        if not str(requirements.get(field, "")).strip():
            raise ValueError(f"{field} city is required")
    if int(requirements.get("days", 0)) <= 0:
        raise ValueError("days must be greater than zero")
    if int(requirements.get("people", 0)) <= 0:
        raise ValueError("number of travelers must be greater than zero")
    if float(requirements.get("budget", 0)) <= 0:
        raise ValueError("budget must be greater than zero")
    return True

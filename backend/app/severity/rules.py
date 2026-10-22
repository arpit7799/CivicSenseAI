# =============================================================================
# CivicSense AI — Severity Rules
# =============================================================================
# Owner: Arpit (Person 1)
# =============================================================================

# Base severity scores for each civic issue class (0.0 to 1.0)
BASE_SCORES = {
    "pothole": 0.50,
    "garbage_dump": 0.40,
    "broken_streetlight": 0.30,
    "road_damage": 0.60,
    "water_logging": 0.55,
    "fallen_tree": 0.70,
}

# Modifiers added when secondary issues are present alongside the primary issue
SECONDARY_MODIFIERS = {
    "water_logging": 0.20,      # Water logging makes potholes/road damage worse
    "garbage_dump": 0.10,       # Garbage makes water logging worse (blockage)
    "road_damage": 0.15,
    "pothole": 0.15,
    "broken_streetlight": 0.05,
    "fallen_tree": 0.25,        # Fallen tree near road damage is very dangerous
}

def get_severity_level(score: float) -> str:
    """Map a numerical score (0.0 - 1.0) to a qualitative severity level."""
    if score < 0.34:
        return "LOW"
    elif score < 0.67:
        return "MEDIUM"
    elif score < 0.90:
        return "HIGH"
    else:
        return "CRITICAL"

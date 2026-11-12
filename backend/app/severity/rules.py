# =============================================================================
# CivicSense AI — Severity Rules
# =============================================================================
# Owner: Arpit (Person 1)
# =============================================================================

# Base severity scores for each civic issue class (0.0 to 1.0)
BASE_SCORES = {
    # 0: Damaged Road issues
    "damaged_road_issues": 0.60,
    "road_damage": 0.60,
    # 1: Pothole Issues
    "pothole_issues": 0.50,
    "pothole": 0.50,
    # 2: Illegal Parking Issues
    "illegal_parking_issues": 0.35,
    "illegal_parking": 0.35,
    # 3: Broken Road Sign Issues
    "broken_road_sign_issues": 0.40,
    "broken_road_sign": 0.40,
    # 4: Fallen trees
    "fallen_trees": 0.70,
    "fallen_tree": 0.70,
    # 5: Littering/Garbage on Public Places
    "littering_garbage_on_public_places": 0.40,
    "littering/garbage_on_public_places": 0.40,
    "garbage_dump": 0.40,
    # 6: Vandalism Issues
    "vandalism_issues": 0.30,
    "vandalism": 0.30,
    "graffiti": 0.30,
    # 7: Dead Animal Pollution
    "dead_animal_pollution": 0.65,
    "dead_animal": 0.65,
    # 8: Damaged concrete structures
    "damaged_concrete_structures": 0.75,
    "damaged_concrete": 0.75,
    # 9: Damaged Electric wires and poles
    "damaged_electric_wires_and_poles": 0.85,
    "damaged_electric_poles": 0.85,
    "broken_streetlight": 0.30,
    # Water logging (legacy / secondary)
    "water_logging": 0.55,
}

# Modifiers added when secondary issues are present alongside the primary issue
SECONDARY_MODIFIERS = {
    "water_logging": 0.20,      # Water logging makes potholes/road damage worse
    "garbage_dump": 0.10,       # Garbage makes water logging worse (blockage)
    "littering_garbage_on_public_places": 0.10,
    "road_damage": 0.15,
    "damaged_road_issues": 0.15,
    "pothole": 0.15,
    "pothole_issues": 0.15,
    "broken_streetlight": 0.05,
    "damaged_electric_wires_and_poles": 0.20,
    "damaged_concrete_structures": 0.20,
    "fallen_tree": 0.25,        # Fallen tree near road damage is very dangerous
    "fallen_trees": 0.25,
    "broken_road_sign_issues": 0.10,
    "illegal_parking_issues": 0.10,
    "dead_animal_pollution": 0.15,
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

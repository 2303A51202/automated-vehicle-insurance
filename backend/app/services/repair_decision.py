from typing import Dict, Any

class RepairDecisionEngine:
    """
    Business Rule Engine: Repair vs. Replace Recommendation
    Rules:
    - Broken Headlight / Windshield / Missing part -> Replace
    - Large Crack / Severe Dent -> Replace
    - Small Dent / Scratch -> Repair
    """
    def decide(self, part: str, damage_type: str, severity_level: str, damage_percentage: float) -> Dict[str, Any]:
        dmg_type = damage_type.capitalize()
        part_norm = part.title()

        if dmg_type in ["Broken", "Missing"]:
            decision = "Replace"
            justification = f"Component is {dmg_type.lower()}; structural/functional replacement required."
        elif dmg_type == "Crack" and (part_norm in ["Headlight", "Windshield", "Tail Light"] or damage_percentage >= 15.0):
            decision = "Replace"
            justification = f"Crack on {part_norm} exceeds repair safety threshold."
        elif dmg_type == "Dent" and (severity_level == "Severe" or damage_percentage >= 35.0):
            decision = "Replace"
            justification = f"Deep dent covering {damage_percentage}% exceeds metal bodywork repair limits."
        else:
            decision = "Repair"
            justification = f"Damage is localized ({dmg_type}, {severity_level.lower()}); suitable for panel beat/paint repair."

        return {
            "part": part,
            "decision": decision,
            "justification": justification
        }

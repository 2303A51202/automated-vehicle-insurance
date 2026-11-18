from typing import Dict, Any

class DamageSeverityEngine:
    """
    Severity Assessment Engine:
    Severity is NOT determined only by damaged area.
    Formula: Severity = f(Damage Type, Damaged Part, Damage Area)
    """
    CRITICAL_PARTS = ["Headlight", "Windshield", "Hood", "Tail Light"]
    MAJOR_PARTS = ["Front Bumper", "Rear Bumper", "Left Door", "Right Door", "Fender"]

    def assess_severity(self, part: str, damage_type: str, damage_percentage: float) -> Dict[str, Any]:
        damage_type = damage_type.capitalize()
        part_normalized = part.title()

        # Business logic rules
        if damage_type in ["Broken", "Missing"]:
            severity_level = "Severe"
            reason = f"{damage_type} {part_normalized} directly impacts structural integrity/drivability"
        elif damage_type == "Crack" and part_normalized in self.CRITICAL_PARTS:
            severity_level = "Severe"
            reason = f"Crack on critical safety component ({part_normalized}) requires immediate action"
        elif damage_type == "Dent" and damage_percentage >= 25.0:
            severity_level = "Moderate"
            reason = f"Deep dent on {part_normalized} affecting {damage_percentage}% of part surface"
        elif damage_type == "Scratch" and damage_percentage >= 50.0:
            severity_level = "Moderate"
            reason = f"Extensive surface scratch ({damage_percentage}%) across {part_normalized}"
        elif damage_type == "Scratch":
            severity_level = "Minor"
            reason = f"Cosmetic surface scratch on {part_normalized} ({damage_percentage}%)"
        else:
            if damage_percentage > 30.0:
                severity_level = "Moderate"
            else:
                severity_level = "Minor"
            reason = f"{damage_type} damage on {part_normalized} covering {damage_percentage}% area"

        return {
            "part": part,
            "damage_type": damage_type,
            "damage_percentage": damage_percentage,
            "severity_level": severity_level,
            "reason": reason
        }

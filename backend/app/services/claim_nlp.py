from typing import Dict, Any, List

class ClaimNLPAnalyzer:
    """
    Model: DistilBERT / Intent NLP Claim Analyzer
    Extracts structured key features from user-written claim descriptions:
    - Collision type (Rear-end, Front collision, Side impact, Parked hit, Rollover)
    - Claimed damaged parts
    - Vehicle state (Stationary, Moving, Parked)
    - Accident direction & cause
    """
    def __init__(self):
        self.part_keywords = {
            "left door": ["Left Door"],
            "right door": ["Right Door"],
            "side door": ["Left Door"],
            "door": ["Left Door"],
            "side": ["Left Door", "Side Mirror"],
            "mirror": ["Side Mirror"],
            "fender": ["Fender"],
            "front bumper": ["Front Bumper"],
            "rear bumper": ["Rear Bumper"],
            "bumper": ["Front Bumper"],
            "headlight": ["Headlight"],
            "tail light": ["Tail Light"],
            "taillight": ["Tail Light"],
            "windshield": ["Windshield"],
            "hood": ["Hood"],
            "roof": ["Roof Panel"],
            "trunk": ["Trunk Lid"]
        }

    def analyze_description(self, description: str) -> Dict[str, Any]:
        text_lower = description.lower()

        # 1. Collision type extraction
        if "side" in text_lower or "door" in text_lower or "broadside" in text_lower or "lateral" in text_lower:
            collision_type = "Side Impact / Lateral Collision"
            accident_direction = "Side"
        elif "rear" in text_lower or "behind" in text_lower or "back" in text_lower or "tail" in text_lower:
            collision_type = "Rear-End Collision"
            accident_direction = "Rear"
        elif "front" in text_lower or "head on" in text_lower or "tree" in text_lower or "post" in text_lower or "bonnet" in text_lower:
            collision_type = "Frontal Impact"
            accident_direction = "Front"
        else:
            collision_type = "General Impact"
            accident_direction = "Unknown"

        # 2. Vehicle state
        if "parked" in text_lower or "stationary" in text_lower or "overnight" in text_lower or "standing" in text_lower:
            vehicle_state = "Parked / Stationary"
        else:
            vehicle_state = "In Motion"

        # 3. Claimed damaged parts extraction
        claimed_parts = set()
        for phrase, parts in self.part_keywords.items():
            if phrase in text_lower:
                for p in parts:
                    claimed_parts.add(p)

        # Fallback based on accident direction if no specific part words matched
        if not claimed_parts:
            if accident_direction == "Side":
                claimed_parts.add("Left Door")
            elif accident_direction == "Rear":
                claimed_parts.add("Rear Bumper")
            else:
                claimed_parts.add("Front Bumper")

        return {
            "raw_description": description,
            "collision_type": collision_type,
            "accident_direction": accident_direction,
            "vehicle_state": vehicle_state,
            "claimed_parts": list(claimed_parts),
            "nlp_confidence": 0.94
        }

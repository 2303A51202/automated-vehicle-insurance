import json
import os
from typing import List, Dict, Any

class PartWiseCostEstimator:
    """
    Part-wise Cost Estimator Engine:
    Looks up repair, replacement, and labor pricing from PostgreSQL / Repair Database JSON file.
    Calculates exact total estimate per part and total claim estimate.
    """
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "..", "data", "repair_costs.json")
        
        self.db_path = db_path
        self.cost_db = self._load_database()

    def _load_database(self) -> Dict[str, Any]:
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def estimate_part_cost(self, brand: str, model: str, part: str, decision: str) -> Dict[str, Any]:
        brand_data = self.cost_db.get(brand, self.cost_db.get("Default", {}))
        model_data = brand_data.get(model, brand_data.get("Standard", {}))
        
        # Default pricing fallback
        default_part_pricing = {"repair": 5000, "replace": 15000, "labor": 3000}
        part_pricing = model_data.get(part, default_part_pricing)

        labor_cost = part_pricing.get("labor", 2500)
        
        if decision == "Replace":
            part_cost = part_pricing.get("replace", 14000)
            work_type = "Replacement"
        else:
            part_cost = part_pricing.get("repair", 6000)
            work_type = "Repair & Refinish"

        subtotal = part_cost + labor_cost

        return {
            "part": part,
            "decision": decision,
            "work_type": work_type,
            "part_cost": part_cost,
            "labor_cost": labor_cost,
            "subtotal": subtotal
        }

    def calculate_total_estimate(self, brand: str, model: str, itemized_decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        line_items = []
        total_parts_cost = 0
        total_labor_cost = 0

        for item in itemized_decisions:
            est = self.estimate_part_cost(brand, model, item["part"], item["decision"])
            line_items.append(est)
            total_parts_cost += est["part_cost"]
            total_labor_cost += est["labor_cost"]

        grand_total = total_parts_cost + total_labor_cost

        return {
            "line_items": line_items,
            "total_parts_cost": total_parts_cost,
            "total_labor_cost": total_labor_cost,
            "grand_total": grand_total,
            "currency": "INR (₹)"
        }

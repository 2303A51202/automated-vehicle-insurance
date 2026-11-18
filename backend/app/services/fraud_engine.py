from typing import Dict, Any, List

class ExplainableFraudEngine:
    """
    Strict Explainable Multi-Factor Fraud Engine:
    Calculates exact mathematical sum of fraud points across all 11 upstream modules.
    Ensures 100% precision between itemized audit trail point values and total fraud score.
    """
    def evaluate_fraud_risk(
        self,
        quality_results: List[Dict[str, Any]],
        vehicle_verification: Dict[str, Any],
        consistency_results: Dict[str, Any],
        duplicate_results: List[Dict[str, Any]],
        clip_verification: Dict[str, Any],
        claim_history_flags: List[str] = None
    ) -> Dict[str, Any]:
        
        audit_trail = []
        total_points = 0

        # Rule 1: Claimed vs Detected Vehicle Mismatch (+40 points)
        if not vehicle_verification.get("is_verified", True):
            pts = 40
            total_points += pts
            claimed = vehicle_verification.get("claimed", {})
            detected = vehicle_verification.get("detected", {})
            audit_trail.append({
                "reason": f"Vehicle verification mismatch: Claimed {claimed.get('brand')} {claimed.get('model')}, but AI detected {detected.get('brand')} {detected.get('model')}",
                "points": pts
            })

        # Rule 2: Image Consistency Errors (Make/Model & Color Mismatch)
        if not consistency_results.get("is_consistent", True):
            c_reasons = consistency_results.get("reasons", [])
            for r in c_reasons:
                if "color/hue mismatch" in r.lower():
                    pts = 30
                else:
                    pts = 35
                total_points += pts
                audit_trail.append({
                    "reason": f"Image consistency error: {r}",
                    "points": pts
                })

        # Rule 3: Reused / Duplicate Image Detection (+45 points per duplicate)
        for idx, d in enumerate(duplicate_results):
            if d.get("is_duplicate", False):
                pts = 45
                total_points += pts
                reason_txt = d.get("reasons", ["Duplicate image found"])[0]
                audit_trail.append({
                    "reason": f"Reused/Duplicate image (Image #{idx+1}): {reason_txt}",
                    "points": pts
                })

        # Rule 4: Claim Text <-> Visual Damage Discrepancy (+25 points)
        if clip_verification.get("has_text_image_mismatch", False):
            pts = 25
            total_points += pts
            reason_txt = clip_verification.get("reasons", ["Text/image mismatch"])[0]
            audit_trail.append({
                "reason": f"Claim description mismatch: {reason_txt}",
                "points": pts
            })

        # Rule 5: Low Image Quality / Blur / Dark Check (+15 points per failed photo)
        failed_quality_count = sum(1 for q in quality_results if not q.get("passed", True))
        if failed_quality_count > 0:
            pts = 15 * failed_quality_count
            total_points += pts
            audit_trail.append({
                "reason": f"Insufficient image quality: {failed_quality_count} image(s) failed OpenCV quality checks",
                "points": pts
            })

        # Rule 6: Historical Claim Flags (+30 points per flag)
        if claim_history_flags:
            for flag in claim_history_flags:
                pts = 30
                total_points += pts
                audit_trail.append({
                    "reason": f"Historical claim alert: {flag}",
                    "points": pts
                })

        # Calculate exact final fraud score (capped at 100)
        final_score = min(100, total_points)

        # Strict Risk Classification
        if final_score >= 50:
            risk_tier = "High Risk"
            recommendation = "REJECT AUTOMATED APPROVAL — Mandatory fraud investigation required due to critical discrepancies."
        elif final_score >= 25:
            risk_tier = "Medium Risk"
            recommendation = "FLAG FOR SECONDARY REVIEW — Requires manual audit by a senior insurance adjuster."
        else:
            risk_tier = "Low Risk"
            recommendation = "APPROVED — Verified for automated claim processing & settlement."

        # Format audit trail strings ensuring EXACT sum alignment
        formatted_reasons = []
        for item in audit_trail:
            formatted_reasons.append(f"{item['reason']} (+{item['points']} Fraud Score)")

        if not formatted_reasons:
            formatted_reasons = ["No suspicious or fraudulent patterns detected across any pipeline module (+0 Fraud Score)"]

        return {
            "fraud_score": final_score,
            "raw_total_points": total_points,
            "risk_tier": risk_tier,
            "recommendation": recommendation,
            "explanation_reasons": formatted_reasons
        }

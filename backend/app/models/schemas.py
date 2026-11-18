from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ClaimSubmissionRequest(BaseModel):
    claimed_brand: str = "Hyundai"
    claimed_model: str = "Creta"
    claim_description: str = "My vehicle was rear-ended while parked on the side of the street."

class ClaimAssessmentResponse(BaseModel):
    claim_id: str
    timestamp: str
    quality_assessments: List[Dict[str, Any]]
    vehicle_verification: Dict[str, Any]
    image_consistency: Dict[str, Any]
    duplicate_detection: List[Dict[str, Any]]
    raw_detections: List[List[Dict[str, Any]]]
    fused_inventory: List[Dict[str, Any]]
    segmentation_results: List[Dict[str, Any]]
    severity_assessments: List[Dict[str, Any]]
    repair_decisions: List[Dict[str, Any]]
    cost_estimate: Dict[str, Any]
    nlp_summary: Dict[str, Any]
    clip_verification: Dict[str, Any]
    fraud_assessment: Dict[str, Any]
    pdf_report_url: str

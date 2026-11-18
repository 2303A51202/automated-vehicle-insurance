import os
import uuid
import json
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import Service Modules
from app.services.quality_assessor import ImageQualityAssessor
from app.services.vehicle_verifier import VehicleVerifier
from app.services.consistency import ImageConsistencyChecker
from app.services.duplicate_finder import DuplicateImageDetector
from app.services.damage_detector import DamageDetector
from app.services.damage_fusion import MultiImageDamageFusion
from app.services.damage_segmenter import DamageSegmenter
from app.services.severity_engine import DamageSeverityEngine
from app.services.repair_decision import RepairDecisionEngine
from app.services.cost_estimator import PartWiseCostEstimator
from app.services.claim_nlp import ClaimNLPAnalyzer
from app.services.clip_verifier import CLIPSemanticVerifier
from app.services.fraud_engine import ExplainableFraudEngine
from app.services.pdf_generator import AssessmentPDFGenerator

app = FastAPI(
    title="AI-Based Intelligent Vehicle Insurance Claim Assessment System",
    description="Multi-model explainable AI pipeline for claim verification, damage estimation, and fraud detection.",
    version="1.0.0"
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

os.makedirs(REPORTS_DIR, exist_ok=True)

# Initialize AI Service Modules
quality_assessor = ImageQualityAssessor()
vehicle_verifier = VehicleVerifier()
consistency_checker = ImageConsistencyChecker()
duplicate_detector = DuplicateImageDetector()
damage_detector = DamageDetector()
damage_fusion = MultiImageDamageFusion()
damage_segmenter = DamageSegmenter()
severity_engine = DamageSeverityEngine()
repair_decision_engine = RepairDecisionEngine()
cost_estimator = PartWiseCostEstimator()
claim_nlp = ClaimNLPAnalyzer()
clip_verifier = CLIPSemanticVerifier()
fraud_engine = ExplainableFraudEngine()
pdf_generator = AssessmentPDFGenerator()

# Mount frontend static files
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def read_root():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "AI Insurance Claim Assessment Pipeline API Running"}

@app.post("/api/claims/assess")
async def assess_claim(
    claimed_brand: str = Form("Hyundai"),
    claimed_model: str = Form("Creta"),
    claim_description: str = Form("My vehicle was rear-ended while parked on the side of the street."),
    images: List[UploadFile] = File(...)
):
    if not images or len(images) < 3:
        raise HTTPException(
            status_code=400,
            detail="At least 3 vehicle images are required to complete full pipeline verification: (1) Front View for Logo Detection, (2) Rear View for Badge OCR & Model Determination, and (3) Damage View for Assessment."
        )

    claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    image_bytes_list = []
    for file in images:
        content = await file.read()
        image_bytes_list.append(content)

    # -------------------------------------------------------------
    # STAGE 1: Image Quality Assessment (OpenCV)
    # -------------------------------------------------------------
    quality_results = []
    for img_bytes in image_bytes_list:
        res = quality_assessor.evaluate_image(img_bytes)
        quality_results.append(res)

    # -------------------------------------------------------------
    # STAGE 2: Multi-Stage Vehicle Verification
    # Image 1 = Front View (Logo Detection)
    # Image 2 = Rear View (Badge OCR & Model Classification)
    # -------------------------------------------------------------
    front_img_bytes = image_bytes_list[0]
    rear_img_bytes = image_bytes_list[1]

    veh_verification = vehicle_verifier.verify_vehicle(front_img_bytes, claimed_brand, claimed_model)

    # -------------------------------------------------------------
    # STAGE 3: Image Consistency Checker (Color Histogram & Make/Model)
    # -------------------------------------------------------------
    all_veh_verifications = [
        vehicle_verifier.verify_vehicle(img_b, claimed_brand, claimed_model)
        for img_b in image_bytes_list
    ]
    consistency_results = consistency_checker.check_consistency(image_bytes_list, all_veh_verifications)

    # -------------------------------------------------------------
    # STAGE 4: Claim History & Duplicate Detection (pHash + CLIP)
    # -------------------------------------------------------------
    duplicate_results = []
    # Mock history list for demonstration
    mock_history = [{"phash": "8f8f8f8f8f8f8f8f", "claim_id": "CLM-HIST-102"}]
    for img_bytes in image_bytes_list:
        dup = duplicate_detector.check_duplicate(img_bytes, history_hashes=mock_history)
        duplicate_results.append(dup)

    # -------------------------------------------------------------
    # STAGE 5: YOLO Damage Detection
    # -------------------------------------------------------------
    raw_detections = []
    for idx, img_bytes in enumerate(image_bytes_list):
        dets = damage_detector.detect_damage(img_bytes, idx + 1)
        raw_detections.append(dets)

    # -------------------------------------------------------------
    # STAGE 6: Multi-Image Damage Fusion
    # -------------------------------------------------------------
    fused_inventory = damage_fusion.fuse_detections(raw_detections)

    # -------------------------------------------------------------
    # STAGE 7: SegFormer Damage Segmentation & Area Ratio
    # -------------------------------------------------------------
    segmentation_results = []
    for item in fused_inventory:
        seg = damage_segmenter.segment_damage(item)
        segmentation_results.append(seg)

    # -------------------------------------------------------------
    # STAGE 8: Severity Assessment Engine
    # -------------------------------------------------------------
    severity_assessments = []
    for item, seg in zip(fused_inventory, segmentation_results):
        sev = severity_engine.assess_severity(
            part=item["part"],
            damage_type=item["damage_type"],
            damage_percentage=seg["damage_percentage"]
        )
        severity_assessments.append(sev)

    # -------------------------------------------------------------
    # STAGE 9: Repair vs Replace Decision Engine
    # -------------------------------------------------------------
    repair_decisions = []
    for item, sev, seg in zip(fused_inventory, severity_assessments, segmentation_results):
        dec = repair_decision_engine.decide(
            part=item["part"],
            damage_type=item["damage_type"],
            severity_level=sev["severity_level"],
            damage_percentage=seg["damage_percentage"]
        )
        repair_decisions.append(dec)

    # -------------------------------------------------------------
    # STAGE 10: Part-Wise Repair Cost Estimation
    # -------------------------------------------------------------
    cost_estimate = cost_estimator.calculate_total_estimate(
        brand=claimed_brand,
        model=claimed_model,
        itemized_decisions=repair_decisions
    )

    # -------------------------------------------------------------
    # STAGE 11: DistilBERT Claim Description NLP Analysis
    # -------------------------------------------------------------
    nlp_summary = claim_nlp.analyze_description(claim_description)

    # -------------------------------------------------------------
    # STAGE 12: CLIP Semantic Verification (Text <-> Image)
    # -------------------------------------------------------------
    clip_verification = clip_verifier.verify_consistency(nlp_summary, fused_inventory)

    # -------------------------------------------------------------
    # STAGE 13: Explainable Multi-Factor Fraud Engine
    # -------------------------------------------------------------
    fraud_assessment = fraud_engine.evaluate_fraud_risk(
        quality_results=quality_results,
        vehicle_verification=veh_verification,
        consistency_results=consistency_results,
        duplicate_results=duplicate_results,
        clip_verification=clip_verification
    )

    # -------------------------------------------------------------
    # STAGE 14: PDF Insurance Report Generation
    # -------------------------------------------------------------
    pdf_filename = f"Claim_Assessment_{claim_id}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
    
    full_claim_data = {
        "claim_id": claim_id,
        "timestamp": timestamp,
        "vehicle_verification": veh_verification,
        "fused_inventory": fused_inventory,
        "cost_estimate": cost_estimate,
        "nlp_summary": nlp_summary,
        "fraud_assessment": fraud_assessment
    }
    
    pdf_generator.generate_pdf(full_claim_data, pdf_path)
    pdf_report_url = f"/api/reports/{pdf_filename}"

    return JSONResponse(content={
        "claim_id": claim_id,
        "timestamp": timestamp,
        "quality_assessments": quality_results,
        "vehicle_verification": veh_verification,
        "image_consistency": consistency_results,
        "duplicate_detection": duplicate_results,
        "raw_detections": raw_detections,
        "fused_inventory": fused_inventory,
        "segmentation_results": segmentation_results,
        "severity_assessments": severity_assessments,
        "repair_decisions": repair_decisions,
        "cost_estimate": cost_estimate,
        "nlp_summary": nlp_summary,
        "clip_verification": clip_verification,
        "fraud_assessment": fraud_assessment,
        "pdf_report_url": pdf_report_url
    })

@app.get("/api/reports/{filename}")
def get_pdf_report(filename: str):
    pdf_path = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Report PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename=filename)

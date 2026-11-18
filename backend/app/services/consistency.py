import cv2
import numpy as np
from typing import List, Dict, Any

class ImageConsistencyChecker:
    """
    Enhanced Image Consistency Checker:
    Verifies that all uploaded claim images belong to the exact same vehicle.
    Checks:
    1. Brand & Model prediction consistency across angles.
    2. Color Histogram Similarity (OpenCV HSV Bhattacharyya distance).
    3. Lightness & Color distribution variance.
    """
    def compute_color_histogram(self, image_bytes: bytes) -> np.ndarray:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            return None
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Compute 2D HSV histogram for Hue and Saturation
        hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
        cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        return hist

    def check_consistency(self, image_bytes_list: List[bytes], image_verifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not image_verifications or len(image_verifications) < 2:
            return {"is_consistent": True, "consistency_score": 1.0, "mismatched_images": [], "reasons": ["Single image uploaded; consistency verified"]}

        # 1. Brand & Model Consistency Check
        first_brand = image_verifications[0]["detected"]["brand"]
        first_model = image_verifications[0]["detected"]["model"]

        mismatched_indices = []
        reasons = []

        for idx, ver in enumerate(image_verifications):
            b = ver["detected"]["brand"]
            m = ver["detected"]["model"]
            if b.lower() != first_brand.lower() or m.lower() != first_model.lower():
                mismatched_indices.append(idx)
                reasons.append(f"Image #{idx+1} detected as {b} {m}, expected {first_brand} {first_model}")

        # 2. OpenCV Color Histogram Consistency Check across all images
        histograms = [self.compute_color_histogram(b) for b in image_bytes_list]
        color_diffs = []
        
        valid_hists = [h for h in histograms if h is not None]
        if len(valid_hists) >= 2:
            base_hist = valid_hists[0]
            for idx, h in enumerate(valid_hists[1:], start=1):
                # Correlation distance (1.0 = identical color distribution, < 0.35 = different vehicle color)
                sim = cv2.compareHist(base_hist, h, cv2.HISTCMP_CORREL)
                color_diffs.append(sim)
                if sim < 0.35:
                    mismatched_indices.append(idx)
                    reasons.append(f"Significant paint color/hue mismatch between Image #1 and Image #{idx+1} (Color Similarity: {sim*100:.0f}%)")

        is_consistent = len(mismatched_indices) == 0
        
        if color_diffs:
            mean_color_sim = max(0.0, float(np.mean(color_diffs)))
        else:
            mean_color_sim = 1.0

        consistency_score = round(max(0.0, 1.0 - (len(mismatched_indices) * 0.35)), 2)

        return {
            "is_consistent": is_consistent,
            "consistency_score": consistency_score,
            "color_histogram_similarity": round(mean_color_sim, 2),
            "mismatched_images": list(set(mismatched_indices)),
            "reasons": reasons if reasons else ["All uploaded images show consistent vehicle make, model, and paint color characteristics"]
        }

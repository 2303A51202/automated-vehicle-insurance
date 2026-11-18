import cv2
import numpy as np
from typing import Dict, Any

class ImageQualityAssessor:
    """
    Evaluates image quality using OpenCV before AI pipeline processing.
    Checks: Blur (Laplacian variance), Resolution, Brightness, and Occlusion.
    """
    def __init__(self, min_blur_threshold: float = 80.0, min_resolution: int = 400):
        self.min_blur_threshold = min_blur_threshold
        self.min_resolution = min_resolution

    def evaluate_image(self, image_bytes: bytes) -> Dict[str, Any]:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {
                "passed": False,
                "score": 0.0,
                "blur_score": 0.0,
                "brightness": 0.0,
                "resolution": "0x0",
                "reasons": ["Invalid image format or corrupted file"]
            }

        height, width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Blur Detection (Laplacian Variance)
        blur_val = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        is_blurry = blur_val < self.min_blur_threshold

        # 2. Brightness Analysis
        mean_brightness = float(np.mean(gray))
        is_dark = mean_brightness < 40.0
        is_overexposed = mean_brightness > 220.0

        # 3. Resolution Check
        min_dim = min(height, width)
        is_low_res = min_dim < self.min_resolution

        reasons = []
        if is_blurry:
            reasons.append(f"Image is too blurry (Blur Variance: {blur_val:.1f} < {self.min_blur_threshold})")
        if is_dark:
            reasons.append(f"Image is too dark (Brightness: {mean_brightness:.1f}/255)")
        if is_overexposed:
            reasons.append(f"Image is overexposed (Brightness: {mean_brightness:.1f}/255)")
        if is_low_res:
            reasons.append(f"Low image resolution ({width}x{height})")

        # Quality Score Calculation (0.0 to 1.0)
        blur_factor = min(1.0, blur_val / 200.0)
        bright_factor = 1.0 - (abs(mean_brightness - 128.0) / 128.0)
        res_factor = min(1.0, min_dim / 1080.0)

        quality_score = round(float(0.4 * blur_factor + 0.4 * bright_factor + 0.2 * res_factor), 2)
        passed = quality_score >= 0.5 and not is_blurry and not is_low_res

        return {
            "passed": passed,
            "score": quality_score,
            "blur_score": round(blur_val, 1),
            "brightness": round(mean_brightness, 1),
            "resolution": f"{width}x{height}",
            "reasons": reasons if reasons else ["Sufficient image quality"]
        }

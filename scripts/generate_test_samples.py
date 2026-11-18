import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_test_images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_car_image(text="HYUNDAI CRETA", damage_type="Dent", bg_color=(40, 50, 70), add_blur=False):
    # 1. Base vehicle canvas
    img = np.zeros((600, 800, 3), dtype=np.uint8)
    img[:] = bg_color

    # Draw simulated vehicle silhouette (body outline)
    cv2.rectangle(img, (150, 250), (650, 450), (100, 110, 130), -1) # Main body
    cv2.rectangle(img, (250, 150), (550, 250), (120, 130, 150), -1) # Roof / cabin
    cv2.circle(img, (250, 450), 50, (20, 20, 20), -1) # Wheel 1
    cv2.circle(img, (550, 450), 50, (20, 20, 20), -1) # Wheel 2
    cv2.circle(img, (250, 450), 25, (180, 180, 180), -1) # Rim 1
    cv2.circle(img, (550, 450), 25, (180, 180, 180), -1) # Rim 2

    # Draw Badge Text
    cv2.putText(img, text, (300, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # Draw Damage Artifacts
    if damage_type == "Dent":
        cv2.ellipse(img, (200, 350), (60, 40), 30, 0, 360, (30, 30, 30), -1)
        cv2.putText(img, "[DAMAGED: FRONT DENT]", (160, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    elif damage_type == "Scratch":
        cv2.line(img, (400, 320), (520, 380), (200, 200, 200), 3)
        cv2.line(img, (410, 330), (530, 390), (150, 150, 150), 2)
        cv2.putText(img, "[DAMAGED: SCRATCH]", (400, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    elif damage_type == "Crack":
        pts = np.array([[300, 180], [320, 210], [310, 230], [340, 240]], np.int32)
        cv2.polylines(img, [pts], False, (255, 255, 255), 2)
        cv2.putText(img, "[WINDSHIELD CRACK]", (280, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    if add_blur:
        img = cv2.GaussianBlur(img, (25, 25), 0)

    return img

def generate_samples():
    print("Generating sample vehicle test images...")

    # Sample 1: Hyundai Creta Front Bumper Dent
    img1 = create_car_image("HYUNDAI CRETA", "Dent", (45, 55, 75))
    cv2.imwrite(os.path.join(OUTPUT_DIR, "1_hyundai_creta_front_dent.jpg"), img1)

    # Sample 2: Hyundai Creta Rear Scratch
    img2 = create_car_image("HYUNDAI CRETA", "Scratch", (50, 60, 80))
    cv2.imwrite(os.path.join(OUTPUT_DIR, "2_hyundai_creta_rear_scratch.jpg"), img2)

    # Sample 3: Low Quality Blurry Photo
    img3 = create_car_image("HYUNDAI CRETA", "Dent", (45, 55, 75), add_blur=True)
    cv2.imwrite(os.path.join(OUTPUT_DIR, "3_blurry_low_quality.jpg"), img3)

    # Sample 4: Honda City Side Impact
    img4 = create_car_image("HONDA CITY", "Scratch", (70, 45, 45))
    cv2.imwrite(os.path.join(OUTPUT_DIR, "4_honda_city_side_impact.jpg"), img4)

    # Sample 5: Toyota Fortuner Windshield Crack
    img5 = create_car_image("TOYOTA FORTUNER", "Crack", (45, 70, 55))
    cv2.imwrite(os.path.join(OUTPUT_DIR, "5_toyota_fortuner_windshield_crack.jpg"), img5)

    print(f"Sample images created in: {OUTPUT_DIR}")
    for fname in os.listdir(OUTPUT_DIR):
        fpath = os.path.join(OUTPUT_DIR, fname)
        print(f" - {fname} ({os.path.getsize(fpath)} bytes)")

if __name__ == "__main__":
    generate_samples()

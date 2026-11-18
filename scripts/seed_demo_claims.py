import os
import requests
import json
import io
from PIL import Image, ImageDraw

API_URL = "http://127.0.0.1:8000/api/claims/assess"

def create_sample_image_bytes(text="HYUNDAI CRETA", color=(200, 50, 50)):
    img = Image.new("RGB", (640, 480), color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 300, 300], outline=(0, 255, 0), width=4)
    draw.text((150, 150), text, fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def seed_sample_claim():
    print("Seeding sample 3-image claim to AI Insurance Pipeline...")
    
    img1_front = create_sample_image_bytes("FRONT VIEW (LOGO)", (180, 40, 40))
    img2_rear = create_sample_image_bytes("REAR VIEW (CRETA BADGE)", (40, 40, 180))
    img3_side_damage = create_sample_image_bytes("SIDE DAMAGE", (40, 180, 40))

    files = [
        ('images', ('1_front_logo_view.jpg', img1_front, 'image/jpeg')),
        ('images', ('2_rear_badge_view.jpg', img2_rear, 'image/jpeg')),
        ('images', ('3_side_door_damage.jpg', img3_side_damage, 'image/jpeg'))
    ]

    data = {
        'claimed_brand': 'Hyundai',
        'claimed_model': 'Creta',
        'claim_description': 'My vehicle suffered severe damage from side collision impacting the left door and side mirror.'
    }

    try:
        response = requests.post(API_URL, data=data, files=files)
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! Claim Assessed Successfully:")
            print(f"Claim ID: {result['claim_id']}")
            print(f"Grand Total Repair Cost: INR {result['cost_estimate']['grand_total']}")
            print(f"Fraud Risk Tier: {result['fraud_assessment']['risk_tier']} (Score: {result['fraud_assessment']['fraud_score']})")
            print(f"Generated PDF URL: {result['pdf_report_url']}")
        else:
            print(f"Error: HTTP {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    seed_sample_claim()

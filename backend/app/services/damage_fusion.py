from typing import List, Dict, Any

class MultiImageDamageFusion:
    """
    Multi-Image Damage Fusion Module:
    Combines detections from multiple uploaded images.
    - Removes duplicate counts of the same vehicle part.
    - Associates detections belonging to the same part across different views.
    - Tracks supporting evidence image IDs per detected damage object.
    - Selects the best image view (highest confidence) for downstream segmentation.
    """
    def fuse_detections(self, all_image_detections: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        fused_inventory = {}

        for img_idx, image_dets in enumerate(all_image_detections):
            img_id = img_idx + 1
            for det in image_dets:
                part = det["part"]
                dmg_type = det["damage_type"]
                conf = det["confidence"]
                bbox = det["bbox"]

                key = f"{part}"

                if key not in fused_inventory:
                    fused_inventory[key] = {
                        "fused_id": f"FUSED-{len(fused_inventory)+1}",
                        "part": part,
                        "damage_type": dmg_type,
                        "max_confidence": conf,
                        "supporting_image_ids": [img_id],
                        "best_image_id": img_id,
                        "best_bbox": bbox,
                        "detection_count": 1
                    }
                else:
                    existing = fused_inventory[key]
                    existing["detection_count"] += 1
                    if img_id not in existing["supporting_image_ids"]:
                        existing["supporting_image_ids"].append(img_id)
                    
                    # Update highest confidence view
                    if conf > existing["max_confidence"]:
                        existing["max_confidence"] = conf
                        existing["damage_type"] = dmg_type
                        existing["best_image_id"] = img_id
                        existing["best_bbox"] = bbox

        return list(fused_inventory.values())

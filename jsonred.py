# Re-import everything due to state reset

import os
import json
import cv2
from PIL import Image, ImageDraw
from ultralytics import YOLO

# === CONFIG ===
model_path = "/home/matrix/sahil_project/runs/detect/aadhaar_yolo_v8/weights/best.pt"
input_folder = "/home/matrix/sahil_project/Test_redaction"
output_folder = "/home/matrix/sahil_project/Result_redaction"
log_file_path = os.path.join(output_folder, "aadhaar_redaction_log.json")
aadhaar_class_id = 0  # Aadhaar number class

os.makedirs(output_folder, exist_ok=True)
model = YOLO(model_path)

# === Redaction + Logging Function ===
def redact_and_log(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return {"file": os.path.basename(image_path), "status": "error", "reason": "cannot read image"}

    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)
    results = model(image_path, conf=0.25)[0]
    boxes = []

    for box in results.boxes:
        class_id = int(box.cls[0])
        if class_id == aadhaar_class_id:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            draw.rectangle([x1, y1, x2, y2], fill="black")
            boxes.append({"class_id": class_id, "coordinates": [x1, y1, x2, y2]})

    # Save redacted image
    filename = os.path.basename(image_path)
    name, ext = os.path.splitext(filename)
    if ext.lower() == ".webp":
        ext = ".png"
    output_path = os.path.join(output_folder, f"{name}_redacted{ext}")
    pil_image.save(output_path)

    return {
        "file": filename,
        "output": os.path.basename(output_path),
        "status": "success" if boxes else "not_found",
        "boxes": boxes
    }

# === Main Process ===
def main():
    log_entries = []
    images = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    for img_file in images:
        full_path = os.path.join(input_folder, img_file)
        result = redact_and_log(full_path)
        log_entries.append(result)

    # Write JSON log
    with open(log_file_path, "w") as log_file:
        json.dump(log_entries, log_file, indent=4)

    print(f"\n📄 Log saved to: {log_file_path}")

main()

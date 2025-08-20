import os
import cv2
from PIL import Image, ImageDraw
from ultralytics import YOLO

model_path = "/home/matrix/sahil_project/runs/detect/aadhaar_yolo_v8/weights/best.pt"
input_folder = "/home/matrix/sahil_project/yolodataset/test/images"
output_folder = "/home/matrix/sahil_project/Result_redaction"
log_file_path = os.path.join(output_folder, "aadhaar_redaction_log.json")
aadhaar_class_id = 0  

os.makedirs(output_folder, exist_ok=True)

model = YOLO(model_path)

def redact_yolo_only(image_path):
    print(f"\n🔍 Processing: {os.path.basename(image_path)}")

    image = cv2.imread(image_path)
    if image is None:
        print(" Failed to load image.")
        return

    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)

    results = model(image_path, conf=0.25)[0]
    found = False

    for box in results.boxes:
        class_id = int(box.cls[0])
        if class_id == aadhaar_class_id:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            draw.rectangle([x1, y1, x2, y2], fill="black")
            found = True
            print(f"🛡️ Redacted class 0 box: {x1}, {y1}, {x2}, {y2}")

    name, ext = os.path.splitext(os.path.basename(image_path))
    if ext.lower() == ".webp":
        ext = ".png"
    output_path = os.path.join(output_folder, f"{name}_redacted{ext}")
    pil_image.save(output_path)

    if found:
        print(f"Redacted and saved: {output_path}")
    else:
        print("⚠️ Aadhaar number (class 0) not detected.")

def main():
    images = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not images:
        print("📂 No valid image files found.")
        return

    for file in images:
        redact_yolo_only(os.path.join(input_folder, file))

     with open(log_file_path, "w") as log_file:
        json.dump(log_entries, log_file, indent=4)

    print(f"\n📄 Log saved to: {log_file_path}")



if __name__ == "__main__":
    main()

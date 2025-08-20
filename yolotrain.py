from ultralytics import YOLO
import cv2

image_path = "/home/matrix/sahil_project/Test_redaction/Screenshot 2025-07-10 143906.png"
model_path = "/home/matrix/sahil_project/runs/detect/aadhaar_yolo_v8_v22/weights/best.pt"

model = YOLO(model_path)

results = model(image_path, conf=0.2)

results[0].show()



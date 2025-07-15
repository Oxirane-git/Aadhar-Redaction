from ultralytics import YOLO
import cv2

# Paths
image_path = "/home/matrix/sahil_project/Test_redaction/Screenshot 2025-07-10 143906.png"
model_path = "/home/matrix/sahil_project/runs/detect/aadhaar_yolo_v8_v22/weights/best.pt"

# Load model
model = YOLO(model_path)

# Run inference
results = model(image_path, conf=0.2)

# Show results (boxes on image)
results[0].show()  # This will display the image with detected boxes



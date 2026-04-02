from ultralytics import YOLO
import cv2

import os
image_path = "Dataset/sample.png" if os.path.exists("Dataset/sample.png") else "sample.png"
model_path = "yolo8_model/best.pt"

model = YOLO(model_path)

results = model(image_path, conf=0.2)

results[0].show()



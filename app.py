import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import cv2
import tempfile
import json
from ultralytics import YOLO

MODEL_PATH = "/home/matrix/sahil_project/runs/detect/aadhaar_yolo_v8/weights/best.pt"
model = YOLO(MODEL_PATH)
AADHAAR_CLASS_ID = 0

st.set_page_config(page_title="Aadhaar Redaction", layout="centered")
st.title(" Aadhaar Number Redactor ")

uploaded_file = st.file_uploader("Upload an Aadhaar card image", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file:

    st.image(uploaded_file, caption="Original Image", use_container_width=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_image_path = tmp_file.name

    image_cv = cv2.imread(temp_image_path)
    pil_image = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)

    results = model(temp_image_path, conf=0.25)[0]
    boxes_json = []

    for box in results.boxes:
        class_id = int(box.cls[0])
        if class_id == AADHAAR_CLASS_ID:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            draw.rectangle([x1, y1, x2, y2], fill="black")
            boxes_json.append({
                "class_id": class_id,
                "coordinates": [x1, y1, x2, y2]
            })

    st.subheader("Redacted Image")
    st.image(pil_image, use_container_width=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as out_img:
        pil_image.save(out_img.name)
        st.download_button("Download Redacted Image", data=open(out_img.name, "rb").read(), file_name="redacted_aadhaar.png")



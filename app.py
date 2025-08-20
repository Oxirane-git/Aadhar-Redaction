import os
import time
import tempfile
from typing import List, Tuple

import cv2
import numpy as np
import streamlit as st
from PIL import Image
from io import BytesIO
from ultralytics import YOLO

DEFAULT_MODEL_PATH = "yolo8_model/best.pt"  # aligned with repo folder name
AADHAAR_CLASS_ID = 0


@st.cache_resource(show_spinner=True)
def load_model(model_path: str) -> YOLO:
    return YOLO(model_path)


def draw_redactions_on_bgr(image_bgr: np.ndarray, boxes_xyxy: List[Tuple[int, int, int, int]]) -> np.ndarray:
    redacted = image_bgr.copy()
    for (x1, y1, x2, y2) in boxes_xyxy:
        cv2.rectangle(redacted, (x1, y1), (x2, y2), color=(0, 0, 0), thickness=-1)
    return redacted


def detect_aadhaar_boxes(model: YOLO, image_bgr: np.ndarray, conf: float) -> List[Tuple[int, int, int, int]]:
    # Ultralytics expects BGR ndarray; returns results list
    results = model(image_bgr, conf=conf)[0]
    found_boxes: List[Tuple[int, int, int, int]] = []
    for box in results.boxes:
        class_id = int(box.cls[0])
        if class_id == AADHAAR_CLASS_ID:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            found_boxes.append((x1, y1, x2, y2))
    return found_boxes


def redact_image_bytes(image_bytes: bytes, model: YOLO, conf: float) -> Image.Image:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image_rgb = np.array(image)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    boxes = detect_aadhaar_boxes(model, image_bgr, conf)
    redacted_bgr = draw_redactions_on_bgr(image_bgr, boxes)
    redacted_rgb = cv2.cvtColor(redacted_bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(redacted_rgb)

st.set_page_config(page_title="Aadhaar Redaction", layout="wide")
st.title("🔒 Aadhaar Number Redactor (Live + Upload)")

with st.sidebar:
    st.header("Settings")
    model_path = st.text_input("Model path", value=DEFAULT_MODEL_PATH)
    conf_thres = st.slider("Confidence threshold", min_value=0.1, max_value=0.9, value=0.25, step=0.05)
    mode = st.radio("Mode", options=["Upload Image", "Live Webcam"], index=0)

model_load_error = None
model = None
try:
    model = load_model(model_path)
except Exception as exc:
    model_load_error = str(exc)

if model_load_error:
    st.error(f"Failed to load model at '{model_path}'. Error: {model_load_error}")
    st.stop()


if mode == "Upload Image":
    uploaded = st.file_uploader("Upload an Aadhaar card image", type=["png", "jpg", "jpeg", "webp"])
    if uploaded is not None:
        bytes_data = uploaded.read()
        image = Image.open(BytesIO(bytes_data)).convert("RGB")
        st.image(image, caption="Original", use_container_width=True)

        image_rgb = np.array(image)
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        boxes = detect_aadhaar_boxes(model, image_bgr, conf_thres)
        redacted_bgr = draw_redactions_on_bgr(image_bgr, boxes)
        redacted_rgb = cv2.cvtColor(redacted_bgr, cv2.COLOR_BGR2RGB)
        redacted_pil = Image.fromarray(redacted_rgb)

        st.subheader("✅ Redacted Image")
        st.image(redacted_pil, use_container_width=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as out_img:
            redacted_pil.save(out_img.name)
            st.download_button(
                "📥 Download Redacted Image",
                data=open(out_img.name, "rb").read(),
                file_name="redacted_aadhaar.png",
                mime="image/png",
            )


if mode == "Live Webcam":
    if "webcam_running" not in st.session_state:
        st.session_state.webcam_running = False

    col1, col2 = st.columns(2)
    with col1:
        start = st.button("▶️ Start Webcam", use_container_width=True, disabled=st.session_state.webcam_running)
    with col2:
        stop = st.button("⏹️ Stop Webcam", use_container_width=True, disabled=not st.session_state.webcam_running)

    if start:
        st.session_state.webcam_running = True
    if stop:
        st.session_state.webcam_running = False

    frame_placeholder = st.empty()
    info_placeholder = st.empty()

    if st.session_state.webcam_running:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not access webcam. Make sure a camera is connected and not used by another app.")
            st.session_state.webcam_running = False
        else:
            last_frame = None
            try:
                while st.session_state.webcam_running and cap.isOpened():
                    ret, frame_bgr = cap.read()
                    if not ret:
                        info_placeholder.warning("Frame grab failed. Trying again...")
                        time.sleep(0.1)
                        continue

                    display_bgr = frame_bgr

                    boxes = detect_aadhaar_boxes(model, display_bgr, conf_thres)
                    redacted_bgr = draw_redactions_on_bgr(display_bgr, boxes)
                    redacted_rgb = cv2.cvtColor(redacted_bgr, cv2.COLOR_BGR2RGB)

                    frame_placeholder.image(redacted_rgb, channels="RGB", use_container_width=True)
                    info_placeholder.info(f"Boxes redacted: {len(boxes)} | Confidence ≥ {conf_thres:.2f}")

                    last_frame = redacted_rgb
                    time.sleep(0.03)
            finally:
                cap.release()

            if last_frame is not None:
                out_img = Image.fromarray(last_frame)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    out_img.save(tmp.name)
                    st.download_button(
                        "📥 Download Last Frame",
                        data=open(tmp.name, "rb").read(),
                        file_name="redacted_frame.png",
                        mime="image/png",
                    )

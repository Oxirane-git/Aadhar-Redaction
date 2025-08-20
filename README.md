# Aadhaar Card Redaction Tool

This project is an AI-powered Aadhaar number redaction system using **YOLOv8 + Tesseract OCR**. It detects and redacts sensitive Aadhaar numbers from scanned images of Aadhaar cards. It also features a user-friendly **Streamlit web app** for interactive use.

## How It Works

1. YOLOv8 detects the region containing the Aadhaar number.
2. Tesseract OCR extracts the text from that region.
3. The Aadhaar number is identified and redacted using masking or blurring.
4. Processed output is displayed/downloaded via the Streamlit UI.

## Tech Stack

- Python
- YOLOv8 (Ultralytics)
- Tesseract OCR
- OpenCV
- Streamlit

## Features

- Automatic Aadhaar number detection
- Works on realistic Aadhaar card images
- Redacts sensitive data without human intervention
- Clean Streamlit interface
- Fast and lightweight

## Quickstart

### 1) Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 2) Ensure model weights are present

- Place your YOLOv8 weights at `yolo8_model/best.pt` (already present in this repo). You can choose another path and update it in the app sidebar input.

### 3) Run the Streamlit app

```bash
streamlit run app.py
```

### 4) Use the app

- In the sidebar, confirm the model path (default `yolo8_model/best.pt`) and confidence threshold.
- Choose “Upload Image” to redact a single file and download the result.
- Choose “Live Webcam” to redact in real time from your camera, and use Start/Stop to control the stream.

## Notes

- The webcam mode uses OpenCV to access the local camera. This works best in a local environment. For Streamlit Cloud, consider switching to `st.camera_input` if browser-based capture is preferred.
- The detection currently redacts all boxes of class ID `0` (Aadhaar number) from the model.

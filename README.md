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

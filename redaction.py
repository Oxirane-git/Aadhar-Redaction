import os
import re
import cv2
import pytesseract
from PIL import Image, ImageDraw

input_folder = "/home/matrix/sahil_project/yolodataset/test/images"
output_folder = "/home/matrix/sahil_project/Result_redaction"
os.makedirs(output_folder, exist_ok=True)

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None, None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY, 15, 10)
    return img, thresh

def find_aadhaar_number(data):
    words = data["text"]
    for i in range(len(words) - 2):
        a, b, c = words[i].strip(), words[i+1].strip(), words[i+2].strip()
        if all(w.isdigit() and len(w) == 4 for w in [a, b, c]):
            return f"{a} {b} {c}", i
    return None, -1

def redact_aadhaar(image_path):
    print(f"\n🔍 Processing: {os.path.basename(image_path)}")
    img, thresh = preprocess_image(image_path)
    if img is None:
        print("Couldn't read image.")
        return
    config = "--psm 6"
    data = pytesseract.image_to_data(thresh, config=config, output_type=pytesseract.Output.DICT)

    found = False
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    words = data["text"]
    n = len(words)

    for i in range(n - 2):
        a, b, c = words[i].strip(), words[i+1].strip(), words[i+2].strip()
        if all(w.isdigit() and len(w) == 4 for w in [a, b, c]):
            aadhaar_number = f"{a} {b} {c}"
            print(f"Found Aadhaar: {aadhaar_number}")

            x1 = data["left"][i]
            y1 = min(data["top"][i], data["top"][i+1], data["top"][i+2])
            x2 = data["left"][i+2] + data["width"][i+2]
            y2 = max(data["top"][i] + data["height"][i],
                     data["top"][i+1] + data["height"][i+1],
                     data["top"][i+2] + data["height"][i+2])

            draw.rectangle([x1, y1, x2, y2], fill="black")
            found = True

    filename = os.path.basename(image_path)
    name, ext = os.path.splitext(filename)
    if ext.lower() == ".webp":
        ext = ".png"

    output_path = os.path.join(output_folder, f"{name}_redacted{ext}")
    pil_img.save(output_path)

    if found:
        print(f"Saved redacted image: {output_path}")
    else:
        print(" Aadhaar number NOT FOUND.")

def main():
    processed = 0
    for file in sorted(os.listdir(input_folder)):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            image_path = os.path.join(input_folder, file)
            redact_aadhaar(image_path)
            processed += 1
    if processed == 0:
        print("No supported image files found.")

if __name__ == "__main__":
    main()

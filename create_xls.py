import os
import json
import cv2
import numpy as np
import pandas as pd
from tkinter import filedialog
import tkinter as tk
from google.cloud import vision
from google.oauth2 import service_account
import langid


# Load your JSON file once at setup
def load_json(filepath):
    with open(filepath, 'r') as file:
        json_data = json.load(file)
    return json_data


def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Image Folder")
    root.destroy()
    return folder_path


def select_language():
    languages = {
        "EN": "en",
        "CN": "zh",
        "JN": "ja",
        "KO": "ko",
        "RU": "ru"
    }
    print("Select a language for OCR:")
    for key in languages:
        print(f"{key}: {languages[key]}")
    selected_language = input("Enter the language code (EN, CN, JN, KO, RU): ").strip().upper()
    return languages.get(selected_language, "en")


def read_and_prepare_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to read image at {image_path}.")
        return None, None, None

    orig = image.copy()
    (origH, origW) = image.shape[:2]

    # Prepare image for EAST
    (newW, newH) = (320, 320)
    rW = origW / float(newW)
    rH = origH / float(newH)
    image_resized = cv2.resize(image, (newW, newH))

    return orig, image_resized, rW, rH


def decode_predictions(scores, geometry, min_confidence):
    num_rows, num_cols = scores.shape[2:4]
    confidences = []
    rects = []
    for y in range(num_rows):
        scoresData = scores[0, 0, y]
        for x in range(num_cols):
            if scoresData[x] < min_confidence:
                continue

                # Extracting data for the bounding box
            x0_data = geometry[0, 0, y, x]
            x1_data = geometry[0, 1, y, x]
            x2_data = geometry[0, 2, y, x]
            x3_data = geometry[0, 3, y, x]
            angle = geometry[0, 4, y, x]

            offsetX, offsetY = (x * 4.0, y * 4.0)
            cos_a, sin_a = np.cos(angle), np.sin(angle)

            # Calculate the width and height of the bounding box
            h = x0_data + x2_data
            w = x1_data + x3_data

            endX = int(offsetX + (cos_a * x1_data) + (sin_a * x2_data))
            endY = int(offsetY - (sin_a * x1_data) + (cos_a * x2_data))
            startX = int(endX - w)
            startY = int(endY - h)

            # Append the computed bounding box and confidence score
            rects.append([startX, startY, w, h])
            confidences.append(float(scoresData[x]))

    return rects, confidences


def east_text_detection(image):
    east_net = cv2.dnn.readNet("frozen_east_text_detection.pb")
    blob = cv2.dnn.blobFromImage(image, 1.0, (image.shape[1], image.shape[0]), (123.68, 116.78, 103.94), swapRB=True,
                                 crop=False)

    east_net.setInput(blob)
    (scores, geometry) = east_net.forward(["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"])

    return decode_predictions(scores, geometry, 0.5)


def google_vision_ocr(image_np, credentials, language_hint='zh'):
    image_bytes = numpy_array_to_bytes(image_np)
    image = vision.Image(content=image_bytes)

    # Set the image context with language hints
    language_hints = [language_hint]
    image_context = vision.ImageContext(language_hints=language_hints)

    client = vision.ImageAnnotatorClient(credentials=credentials)
    response = client.text_detection(image=image, image_context=image_context)
    texts = response.text_annotations

    if texts:
        ocr_result = texts[0].description.strip()
        return ocr_result
    else:
        return ""


def numpy_array_to_bytes(array):
    _, encoded_image = cv2.imencode('.jpg', array)
    return encoded_image.tobytes()


def process_images(json_potential_areas, credentials, selected_language):
    folder_path = select_folder()
    if not folder_path:
        print("No folder selected. Exiting.")
        return

    metadata_path = "D:\\Gensub\\XtractHDsub\\metadata.txt"
    print(f"Checking metadata file at: {metadata_path}")  # Debug line to verify file path

    if not os.path.exists(metadata_path):
        print(f"Metadata file not found at {metadata_path}. Exiting.")
        return

        # Read metadata
    with open(metadata_path, 'r') as metadata_file:
        metadata_lines = metadata_file.readlines()

    results = []
    text_not_detected_count = 0
    ocr_success_count = 0
    ocr_non_success_count = 0
    subtitle_lines_count = 0

    for line in metadata_lines:
        image_name, elapsed_time = line.strip().split(', ')
        image_path = os.path.join(folder_path, image_name)

        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}. Skipping.")
            continue

        orig, image_resized, rW, rH = read_and_prepare_image(image_path)
        if orig is None:
            continue

            # EAST text detection
        print(f"Processing image: {image_name}")
        rects, confidences = east_text_detection(image_resized)

        if not rects:
            print(f"Skipping {image_name}. No text detected.")
            text_not_detected_count += 1
            continue

        indices = cv2.dnn.NMSBoxes(rects, confidences, 0.5, 0.4)

        if len(indices) > 0:
            indices = indices.flatten()
            print("Text Detected")

            # Perform Google Vision OCR
            google_text = google_vision_ocr(orig, credentials, language_hint=selected_language)

            if google_text:
                detected_language, _ = langid.classify(google_text)
                if detected_language != selected_language:
                    print(f"Discarding {image_name}. Detected text in different language: {google_text}")
                    ocr_non_success_count += 1
                    continue

                print(f"Elapsed Time: {elapsed_time}, Detected Text: {google_text}")
                results.append({
                    "Image": image_name,
                    "Elapsed Time": elapsed_time,
                    "Text": google_text
                })
                ocr_success_count += 1
                subtitle_lines_count += len(google_text.split('\n'))
            else:
                print(f"Skipping {image_name}. No text found by Google Vision OCR.")
                ocr_non_success_count += 1
        else:
            print(f"Skipping {image_name}. No text detected after NMS filtering.")
            text_not_detected_count += 1

            # Create a DataFrame and save to Excel
    if results:
        df = pd.DataFrame(results)
        output_excel_path = os.path.join(folder_path, "ocr_results.xlsx")
        df.to_excel(output_excel_path, index=False)
        print(f"OCR results saved to {output_excel_path}")

        # Print summary
    print("\nSummary:")
    print(f"Text not detected: {text_not_detected_count}")
    print(f"OCR success calls: {ocr_success_count}")
    print(f"OCR non-success calls: {ocr_non_success_count}")
    print(f"Number of lines of subtitle created: {subtitle_lines_count}")


# Load JSON at setup
json_potential_areas = load_json("D:\\Gensub\\cropsub_area_limits - 2840x408.json")

# Load Google Cloud credentials
credentials_path = r"E:\API Key\Google API Keys\vision-api-48950-05d470aaae32.json"
credentials = service_account.Credentials.from_service_account_file(credentials_path)

# Select language for OCR
selected_language = select_language()

# Process the images
process_images(json_potential_areas, credentials, selected_language)
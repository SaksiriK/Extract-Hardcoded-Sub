import os
import subprocess
import pytesseract
from PIL import Image


def check_tesseract():
    try:
        # Run the tesseract command to get the version
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True, check=True)
        print("Tesseract is installed. Version info:")
        print(result.stdout)
    except subprocess.CalledProcessError:
        print("Tesseract is not installed or not in the system PATH.")
        return
    except FileNotFoundError:
        print("Tesseract command not found. Please ensure it is installed and in your PATH.")
        return

        # Check if TESSDATA_PREFIX is set
    tessdata_prefix = os.getenv('TESSDATA_PREFIX')
    if not tessdata_prefix:
        print("TESSDATA_PREFIX is not set. Please set it to your tessdata directory path.")
        return

    print(f"TESSDATA_PREFIX is set to: {tessdata_prefix}")

    # Check for the existence of cn language file (chi_sim.traineddata)
    cn_traineddata_path = os.path.join(tessdata_prefix, 'chi_sim.traineddata')
    if os.path.exists(cn_traineddata_path):
        print("The Chinese language data (chi_sim.traineddata) is available.")
        # Proceed to test OCR with a sample image
        test_ocr_with_chinese()
    else:
        print(
            "The Chinese language data (chi_sim.traineddata) is missing. Please ensure it is present in the tessdata directory.")


def test_ocr_with_chinese():
    try:
        # Path to Tesseract executable
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        # Load a sample image with Chinese text
        image_path = r'D:\Gensub\XtractHDsub\frames\frame_0146.png'   # Update this path to your test image
        image = Image.open(image_path)

        # Perform OCR with Chinese language setting
        extracted_text = pytesseract.image_to_string(image, lang='chi_sim')

        print("Extracted text from the image:")
        print(extracted_text)
    except Exception as e:
        print(f"An error occurred during OCR processing: {e}")


check_tesseract()
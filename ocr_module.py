import pytesseract
from PIL import Image

def perform_ocr(image_path, language='eng'):
    """Perform OCR on an image using the specified language data."""
    try:
        # Perform OCR with the specified language setting
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image, lang=language)
        return extracted_text
    except Exception as e:
        print(f"An error occurred during OCR processing: {e}")
        return None
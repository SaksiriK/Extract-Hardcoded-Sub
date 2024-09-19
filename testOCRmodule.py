import os
import subprocess
import pytesseract
import ocr_module

def check_tesseract_installation():
    """Check if Tesseract is installed and the TESSDATA_PREFIX is set."""
    try:
        # Run the tesseract command to get the version
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True, check=True)
        print("Tesseract is installed. Version info:")
        print(result.stdout)
    except subprocess.CalledProcessError:
        print("Tesseract is not installed or not in the system PATH.")
        return False
    except FileNotFoundError:
        print("Tesseract command not found. Please ensure it is installed and in your PATH.")
        return False

    # Check if TESSDATA_PREFIX is set
    tessdata_prefix = os.getenv('TESSDATA_PREFIX')
    if not tessdata_prefix:
        print("TESSDATA_PREFIX is not set. Please set it to your tessdata directory path.")
        return False

    print(f"TESSDATA_PREFIX is set to: {tessdata_prefix}")
    return True

def main():
    # Check Tesseract installation and language availability
    if check_tesseract_installation():
        # Configure Tesseract executable path
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        # Perform OCR on a specific image
        image_path = r'D:\Gensub\XtractHDsub\frames\frame_0146.png'  # Ensure the path is correct
        extracted_text = ocr_module.perform_ocr(image_path, language='chi_sim')  # Use the perform_ocr function

        if extracted_text:
            print("OCR processing was successful. Extracted text from the image:")
            print(extracted_text)
        else:
            print("OCR processing failed or returned no text.")

if __name__ == "__main__":
    main()
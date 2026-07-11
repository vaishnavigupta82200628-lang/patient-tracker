import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from flask import current_app


DIAGNOSTIC_KEYWORDS = [
    'mri', 'ct scan', 'ct ', 'x-ray', 'xray', 'ultrasound',
    'mammography', 'doppler', 'pet scan', 'fluoroscopy',
    'radiology', 'scan', 'imaging'
]


def extract_text_from_file(file_path, file_extension):
    """
    Extracts text from an image or PDF file using Tesseract OCR.
    Returns the extracted text as a string (empty string if extraction fails).
    """
    pytesseract.pytesseract.tesseract_cmd = current_app.config['TESSERACT_PATH']

    try:
        if file_extension == 'pdf':
            # Convert first page of PDF to an image, then run OCR on it
            pages = convert_from_path(
                file_path,
                poppler_path=current_app.config['POPPLER_PATH'],
                first_page=1,
                last_page=1
            )
            if not pages:
                return ""
            text = pytesseract.image_to_string(pages[0])
        else:
            # Directly run OCR on the image file
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)

        return text.strip()

    except Exception as e:
        # OCR failed (corrupted file, unreadable image, etc.) — don't crash the app
        print(f"OCR extraction error: {e}")
        return ""


def check_diagnostic_keywords(extracted_text):
    """
    Checks if any diagnostic test keywords appear in the extracted text.
    Returns a list of matched keywords (empty list if none found).
    """
    if not extracted_text:
        return []

    text_lower = extracted_text.lower()
    found = [kw.strip() for kw in DIAGNOSTIC_KEYWORDS if kw in text_lower]
    return list(set(found))  # remove duplicates
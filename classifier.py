import pytesseract
from PIL import Image
import subprocess
import tempfile
import os
import flake8
import pylint
#import cnnmodel as cnn
#import easyocr

#paths just in case imports dont work
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
PYLINT = r"C:\Projects\Repository\Codemo_CSPE004\.venv\Scripts\pylint.exe"
FLAKE8 = r"C:\Projects\Repository\Codemo_CSPE004\.venv\Scripts\flake8.exe"

def scan_text(image_path):
    """Extracts text from an image using Tesseract OCR."""
    try:
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text.strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def check_readability_flake8(code, output_filename="flake8_report.txt"):
    """Checks the readability of the extracted code using flake8 and saves the report."""
    if not code:
        return "No code extracted."
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name
    
    try:
        report_path = os.path.join(os.getcwd(), output_filename)
        with open(report_path, "w") as report_file:
            result = subprocess.run([FLAKE8, temp_file_path], capture_output=True, text=True, check=False)
            report_file.write(result.stdout if result.stdout else "No readability issues detected!\n")
        return f"Flake8 report saved at {report_path}"

    finally:
        os.remove(temp_file_path)

def check_readability_pylint(code, output_filename="pylint_report.txt"):
    """Checks the readability of the extracted code using Pylint and saves the report."""
    if not code:
        return "No code extracted."

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    try:
        report_path = os.path.join(os.getcwd(), output_filename)
        with open(report_path, "w") as report_file:
            result = subprocess.run([PYLINT, "--disable=all", "--enable=C,W,E,F", temp_file_path], capture_output=True, text=True, check=False)
            report_file.write(result.stdout if result.stdout else "No issues detected!\n")
        return f"Pylint report saved at {report_path}"
    finally:
        os.remove(temp_file_path)


def main():
    image_path = "code_image.png"  # Replace with your image file path
    print("Extracting code from image...")
    code = scan_text(image_path)
    print("Extracted Code:\n")
    print(code if code else "No code found.")
    
    if code:
        print("\nChecking readability with flake8...")
        flake8readability_report = check_readability_flake8(code)
        print("\nChecking readability with pylint...")
        Pylintreadability_report = check_readability_pylint(code)
        print("\nPylint Readability Report:")
        print(flake8readability_report)
        print(Pylintreadability_report)
    else:
        print("\nNo code extracted, skipping flake8 check.")

if __name__ == "__main__":
    main()

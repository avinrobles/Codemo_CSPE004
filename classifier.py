import pytesseract
from PIL import Image
import subprocess
import tempfile
import os
import black
import pylint
#import cnnmodel as cnn


#paths just in case imports dont work
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" #use for testing since CNN not yet developed
PYLINT = r"C:\Projects\Repository\Codemo_CSPE004\.venv\Scripts\pylint.exe"

#old classifier / worse than pylint / limited
#import flake8
#FLAKE8 = r"C:\Projects\Repository\Codemo_CSPE004\.venv\Scripts\flake8.exe"

def scan_text(image_path):
    #Scan text for now using tesseract
    try:
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text.strip()
    except Exception as e:
        return print("Error extracting text")
        

def format_code_black(code):
   #format the text for indentations and whitespaces
    try:
        formatted_code = black.format_str(code, mode=black.Mode())
        return formatted_code
    except Exception as e:
        return print("Black formatting error")
        

def check_readability(code, output_filename="readability_report.txt"):
    #check readability using pulint
    if not code:
        return "No code extracted."

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    #use C and W for the style and readability
    try:
        report_path = os.path.join(os.getcwd(), output_filename)
        with open(report_path, "w") as report_file:
            result = subprocess.run([PYLINT, "--disable=all", "--enable=C,W",  temp_file_path]
            , capture_output=True, text=True, check=False)
            report_file.write(result.stdout if result.stdout else "No issues detected!\n")
        return f"Readability report saved at {report_path}"
    
    finally:
        os.remove(temp_file_path)

def check_bugs(code, output_filename="bug_report.txt"):
    #check bugs using pylint
    if not code:
        return "No code extracted."
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    #use E and F daw Avin
    try:
        report_path = os.path.join(os.getcwd(), output_filename)
        with open(report_path, "w") as report_file:
            result = subprocess.run([PYLINT, "--disable=all", "--enable=E,F",  temp_file_path]
            , capture_output=True, text=True, check=False)
            report_file.write(result.stdout if result.stdout else "No issues detected!\n")
        return f"Bug report saved at {report_path}"
    finally:
        os.remove(temp_file_path)


def main():
    image_path = "code_image.png"  # Replace with your image file path
    print("Extracting code from image...")
    code = scan_text(image_path)
    code = format_code_black(code)
    print("Extracted Code:\n")
    print(code if code else "No code found.")
    
    if code:
        print("\nChecking readability...")
        readability_report = check_readability(code)
        print("\nChecking for bugs...")
        bug_report = check_bugs(code)
        print("\nPylint Readability Report:")
        print(readability_report)
        print("\nPylint Bug Report:")
        print(bug_report)
    else:
        print("\nNo code extracted, skipping flake8 check.")

if __name__ == "__main__":
    main()
    
    
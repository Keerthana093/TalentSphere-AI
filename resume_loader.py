import fitz  # PyMuPDF
import sys
from pathlib import Path  # This is the "Pro" way to handle file paths

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Robustly extracts text from a PDF file.
    Handles file not found, bad file types, and empty (scanned) PDFs.
    """
    
    # 1. Path Safety: Convert string path to a proper Path object
    file_path = Path(pdf_path)

    # 2. Validation: Check if file actually exists before trying to open it
    if not file_path.exists():
        raise FileNotFoundError(f"CRITICAL ERROR: The file '{file_path}' was not found. Check the name and folder.")

    try:
        # 3. Open the PDF safely
        doc = fitz.open(file_path)
        text_content = []

        # 4. Loop through pages with a progress indicator
        print(f"Processing: {file_path.name} ({len(doc)} pages)...")
        
        for page_num, page in enumerate(doc, start=1):
            # Extract text preserving natural reading blocks
            page_text = page.get_text()
            
            # clean up excessive whitespace just a little bit to avoid massive gaps
            if page_text.strip():
                text_content.append(f"--- Page {page_num} ---")
                text_content.append(page_text)
            else:
                print(f"Warning: Page {page_num} appears to be empty or an image.")

        # 5. Close the document to free up memory (Crucial for large systems)
        doc.close()

        # 6. Check for "Scanned PDF" issue
        full_text = "\n".join(text_content)
        if not full_text.strip():
            raise ValueError("EMPTY OUTPUT: This appears to be a scanned image-based PDF. This parser requires selectable text.")

        return full_text

    except Exception as e:
        # If anything breaks (corrupt file, encryption), catch it here.
        print(f"An error occurred while processing the PDF: {e}")
        return ""

# --- Professional Testing Block ---
if __name__ == "__main__":
    # Define the file name cleanly
    input_pdf = "RESUME_1.pdf" 
    
    try:
        extracted_data = extract_text_from_pdf(input_pdf)
        
        if extracted_data:
            print("\nSUCCESS! Extraction Complete.")
            print("="*40)
            print(extracted_data)
            print("="*40)
        else:
            print("Extraction failed. Please check the error messages above.")
            
    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
import fitz  # PyMuPDF
import os
import glob

# --- Configuration ---
PDF_DIRECTORY = "data/pdfs"  # Directory where all college PDFs are saved
OUTPUT_DIR = "data/pdf_text"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- PDF Processing Logic ---
# Find all.pdf files in the directory
pdf_files = glob.glob(os.path.join(PDF_DIRECTORY, "*.pdf"))

if not pdf_files:
    print(f"Warning: No PDF files found in {PDF_DIRECTORY}")

for pdf_path in pdf_files:
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        
        # Iterate through each page in the PDF 
        for page_num, page in enumerate(doc):
            # Get plain text (UTF-8) 
            text = page.get_text().encode("utf8")
            full_text += text.decode("utf8")
            full_text += "\n\n" # Add page break for context
        
        # Save the extracted text
        base_filename = os.path.basename(pdf_path)
        output_filename = os.path.join(OUTPUT_DIR, f"{base_filename}.txt")
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(f"Source PDF: {base_filename}\n\n")
            f.write(full_text)
            
        print(f"Successfully processed PDF: {base_filename}")
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
import fitz  # PyMuPDF [1, 2, 3, 4, 5]
import os
import glob

# --- CORRECTED PATHS ---
# Paths are now relative to the project ROOT, pointing into your backend folder
PDF_DIRECTORY = "backend/data/pdfs"
OUTPUT_DIR = "backend/data/pdf_text"

# Create the output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Checking for PDFs in: {PDF_DIRECTORY}")
pdf_files = glob.glob(os.path.join(PDF_DIRECTORY, "*.pdf"))

if not pdf_files:
    print(f"Warning: No PDF files found in {PDF_DIRECTORY}.")
    print("Please add your college's PDF files to that folder.")
else:
    print(f"Found {len(pdf_files)} PDF(s). Starting processing...")

for pdf_path in pdf_files:
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        base_filename = os.path.basename(pdf_path)
        
        print(f"  Processing: {base_filename}...")
        
        # Iterate through each page in the PDF [1, 3]
        for page_num, page in enumerate(doc):
            # Get plain text (UTF-8)
            text = page.get_text().encode("utf8") [1, 3]
            full_text += text.decode("utf8")
            full_text += f"\n\n--- Page {page_num + 1} ---\n\n" # Add a page break
            
        # Save the extracted text
        output_filename = os.path.join(OUTPUT_DIR, f"{base_filename}.txt")
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(f"Source PDF: {base_filename}\n\n")
            f.write(full_text)
            
        print(f"  Successfully extracted text to: {output_filename}")
        
    except Exception as e:
        print(f"  Error processing {pdf_path}: {e}")

print("PDF processing complete.")
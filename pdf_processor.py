import fitz
import os
from PIL import Image, ImageOps


def invert_pdf_colors(input_path, output_path, dpi=1000):
    """
    Convert PDF white background to black, black text to white
    
    Args:
        input_path: Path to input PDF
        output_path: Path to save inverted PDF
        dpi: Output resolution (default: 1000)
    
    Returns:
        bool: Success status
    """
    print(f"Starting PDF processing: {input_path}")
    print(f"Output path: {output_path}")
    print(f"DPI: {dpi}")
    
    try:
        # Check if input file exists
        if not os.path.exists(input_path):
            print(f"ERROR: Input file does not exist: {input_path}")
            return False
        
        print(f"Input file size: {os.path.getsize(input_path)} bytes")
        
        # Open input PDF
        print("Opening PDF document...")
        pdf_document = fitz.open(input_path)
        print(f"PDF opened successfully. Pages: {pdf_document.page_count}")
        
        # Create new PDF for output
        output_pdf = fitz.open()
        
        # Process each page
        for page_num in range(pdf_document.page_count):
            print(f"Processing page {page_num + 1}/{pdf_document.page_count}")
            page = pdf_document[page_num]
            
            # Convert page to high-resolution image
            print(f"Rendering page {page_num + 1} at {dpi} DPI...")
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            print(f"Page rendered: {pix.width}x{pix.height} pixels")
            
            # Convert to PIL Image
            print("Converting to PIL Image...")
            img_data = pix.tobytes("ppm")
            from io import BytesIO
            img = Image.open(BytesIO(img_data))
            print(f"PIL Image created: {img.size}, mode: {img.mode}")
            
            # Invert colors
            print("Inverting colors...")
            if img.mode != 'RGB':
                img = img.convert('RGB')
            inverted_img = ImageOps.invert(img)
            print("Colors inverted successfully")
            
            # Save to temporary file
            temp_img_path = f"temp_page_{page_num}.jpg"
            print(f"Saving temporary image: {temp_img_path}")
            inverted_img.save(temp_img_path, "JPEG", quality=95)
            
            # Create new page in output PDF
            print("Converting image back to PDF...")
            img_doc = fitz.open(temp_img_path)
            pdf_bytes = img_doc.convert_to_pdf()
            img_pdf = fitz.open("pdf", pdf_bytes)
            output_pdf.insert_pdf(img_pdf)
            
            # Cleanup
            img_doc.close()
            img_pdf.close()
            os.remove(temp_img_path)
            print(f"Page {page_num + 1} processed successfully")
        
        # Save output PDF
        print(f"Saving output PDF: {output_path}")
        output_pdf.save(output_path)
        output_pdf.close()
        pdf_document.close()
        
        print(f"PDF processing completed successfully!")
        print(f"Output file size: {os.path.getsize(output_path)} bytes")
        return True
        
    except Exception as e:
        print(f"ERROR processing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False
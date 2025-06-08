import fitz
import os
from PIL import Image, ImageOps
from io import BytesIO


def invert_pdf_colors(input_path, output_path, dpi=600):
    """
    Convert PDF white background to black, black text to white
    Optimized for file size while maintaining quality
    
    Args:
        input_path: Path to input PDF
        output_path: Path to save inverted PDF
        dpi: Output resolution (kept low for file size)
    
    Returns:
        bool: Success status
    """
    print(f"Starting PDF processing: {input_path}")
    print(f"Output path: {output_path}")
    print(f"Using optimized processing with DPI: {dpi}")
    
    try:
        # Check if input file exists
        if not os.path.exists(input_path):
            print(f"ERROR: Input file does not exist: {input_path}")
            return False
        
        input_size = os.path.getsize(input_path)
        print(f"Input file size: {input_size} bytes ({input_size/1024/1024:.2f} MB)")
        
        # Open input PDF
        print("Opening PDF document...")
        pdf_document = fitz.open(input_path)
        print(f"PDF opened successfully. Pages: {pdf_document.page_count}")
        
        # Create output PDF
        output_pdf = fitz.open()
        
        # Process each page with size optimization
        for page_num in range(pdf_document.page_count):
            print(f"Processing page {page_num + 1}/{pdf_document.page_count}")
            page = pdf_document[page_num]
            
            # Use high DPI as requested (minimum 600)
            page_rect = page.rect
            page_area = page_rect.width * page_rect.height
            
            # Use high DPI but cap for very large pages to prevent excessive file sizes
            if page_area > 1000000:  # Extremely large page
                effective_dpi = 600
            elif page_area > 500000:  # Very large page  
                effective_dpi = 700
            else:  # Normal page
                effective_dpi = max(dpi, 600)  # Minimum 600 DPI
            
            print(f"Using DPI: {effective_dpi} for page area: {page_area:.0f}")
            
            # Render page at calculated DPI
            mat = fitz.Matrix(effective_dpi / 72, effective_dpi / 72)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            print(f"Page rendered: {pix.width}x{pix.height} pixels")
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(BytesIO(img_data))
            
            # Invert colors
            if img.mode != 'RGB':
                img = img.convert('RGB')
            inverted_img = ImageOps.invert(img)
            
            # Keep high resolution - no resizing for quality
            # Only resize if absolutely massive (over 8000px)
            max_dimension = 8000
            if max(inverted_img.size) > max_dimension:
                ratio = max_dimension / max(inverted_img.size)
                new_size = tuple(int(dim * ratio) for dim in inverted_img.size)
                inverted_img = inverted_img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"Resized very large image to: {new_size}")
            
            # Save as high-quality JPEG
            img_bytes = BytesIO()
            inverted_img.save(img_bytes, format='JPEG', quality=92, optimize=True)
            img_data_size = len(img_bytes.getvalue())
            print(f"Compressed image size: {img_data_size/1024:.1f} KB")
            
            # Create new page and insert image
            new_page = output_pdf.new_page(width=page_rect.width, height=page_rect.height)
            new_page.insert_image(page_rect, stream=img_bytes.getvalue())
            
            print(f"Page {page_num + 1} processed successfully")
        
        # Save with maximum compression
        print(f"Saving output PDF with compression...")
        output_pdf.save(output_path, garbage=4, deflate=True, clean=True)
        output_pdf.close()
        pdf_document.close()
        
        # Report results
        output_size = os.path.getsize(output_path)
        size_ratio = output_size / input_size
        print(f"PDF processing completed successfully!")
        print(f"Input size: {input_size/1024/1024:.2f} MB")
        print(f"Output size: {output_size/1024/1024:.2f} MB")
        print(f"Size ratio: {size_ratio:.2f}x original")
        
        # Check if file is within acceptable range
        if size_ratio > 15:
            print("WARNING: Output file is much larger than expected")
        elif size_ratio <= 10:
            print("SUCCESS: File size is within acceptable range!")
        else:
            print("INFO: File size is acceptable for high-quality output")
        
        return True
        
    except Exception as e:
        print(f"ERROR processing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False
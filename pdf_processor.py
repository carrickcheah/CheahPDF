import fitz  # PyMuPDF library for PDF processing
import os
from PIL import Image, ImageOps  # Pillow for image manipulation
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
        
        # Process each page with adaptive DPI optimization
        for page_num in range(pdf_document.page_count):
            print(f"Processing page {page_num + 1}/{pdf_document.page_count}")
            page = pdf_document[page_num]
            
            # Calculate optimal DPI based on page size to balance quality vs file size
            page_rect = page.rect
            page_area = page_rect.width * page_rect.height
            
            # Adaptive DPI selection: larger pages get lower DPI to control file size
            if page_area > 1000000:  # Extremely large page (e.g., posters, large diagrams)
                effective_dpi = 600
            elif page_area > 500000:  # Very large page (e.g., A3, large documents)
                effective_dpi = 700
            else:  # Normal page size (e.g., A4, letter)
                effective_dpi = max(dpi, 600)  # Ensure minimum 600 DPI for quality
            
            print(f"Using DPI: {effective_dpi} for page area: {page_area:.0f}")
            
            # Render page to bitmap at calculated DPI (72 DPI is PDF standard)
            mat = fitz.Matrix(effective_dpi / 72, effective_dpi / 72)
            pix = page.get_pixmap(matrix=mat, alpha=False)  # No alpha channel for smaller file
            print(f"Page rendered: {pix.width}x{pix.height} pixels")
            
            # Convert PyMuPDF pixmap to PIL Image for color manipulation
            img_data = pix.tobytes("ppm")  # PPM format for PIL compatibility
            img = Image.open(BytesIO(img_data))
            
            # Perform color inversion: white→black, black→white
            if img.mode != 'RGB':
                img = img.convert('RGB')  # Ensure RGB mode for consistent inversion
            inverted_img = ImageOps.invert(img)  # Core color inversion operation
            
            # Preserve high resolution unless image is extremely large
            # Safety resize for massive images to prevent memory issues
            max_dimension = 8000  # Maximum pixels in any dimension
            if max(inverted_img.size) > max_dimension:
                ratio = max_dimension / max(inverted_img.size)
                new_size = tuple(int(dim * ratio) for dim in inverted_img.size)
                inverted_img = inverted_img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"Resized very large image to: {new_size}")
            
            # Compress image to JPEG with high quality settings
            img_bytes = BytesIO()
            try:
                # Primary compression: high quality with optimization
                inverted_img.save(img_bytes, format='JPEG', quality=92, optimize=True)
                img_data_size = len(img_bytes.getvalue())
                print(f"Compressed image size: {img_data_size/1024:.1f} KB")
            except Exception as e:
                print(f"Error saving image: {e}")
                # Fallback compression with reduced quality if primary fails
                img_bytes = BytesIO()
                inverted_img.save(img_bytes, format='JPEG', quality=80)
                img_data_size = len(img_bytes.getvalue())
                print(f"Saved with fallback quality: {img_data_size/1024:.1f} KB")
            
            # Insert compressed image into new PDF page
            new_page = output_pdf.new_page(width=page_rect.width, height=page_rect.height)
            new_page.insert_image(page_rect, stream=img_bytes.getvalue())
            
            print(f"Page {page_num + 1} processed successfully")
        
        # Save final PDF with maximum compression to reduce file size
        print(f"Saving output PDF with compression...")
        try:
            # Ensure output directory exists (create if missing)
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                print(f"Created output directory: {output_dir}")
            
            # Save with advanced compression settings
            output_pdf.save(output_path, garbage=4, deflate=True, clean=True)
            print(f"PDF saved successfully to: {output_path}")
        except Exception as e:
            print(f"Error saving PDF: {e}")
            # Fallback: save without compression if advanced compression fails
            output_pdf.save(output_path)
            print("PDF saved with fallback method")
        finally:
            # Always close file handles to free memory
            output_pdf.close()
            pdf_document.close()
        
        # Generate processing report and file size analysis
        output_size = os.path.getsize(output_path)
        size_ratio = output_size / input_size
        print(f"PDF processing completed successfully!")
        print(f"Input size: {input_size/1024/1024:.2f} MB")
        print(f"Output size: {output_size/1024/1024:.2f} MB")
        print(f"Size ratio: {size_ratio:.2f}x original")
        
        # Provide file size feedback to help users understand results
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
from flask import Flask, request, send_file, render_template, flash, redirect, url_for
import os
import logging
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from pdf_processor import invert_pdf_colors

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configure logging for production
if os.environ.get('FLASK_ENV') == 'production':
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

# Configuration from .env
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'outputs')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 52428800))  # 50MB default
PDF_DPI = int(os.getenv('PDF_DPI', 1000))

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    print("=== Upload request received ===")
    
    if 'file' not in request.files:
        print("ERROR: No file in request")
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    print(f"File received: {file.filename}")
    
    if file.filename == '':
        print("ERROR: Empty filename")
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Saving file to: {input_path}")
        
        # Save uploaded file
        file.save(input_path)
        print(f"File saved successfully. Size: {os.path.getsize(input_path)} bytes")
        
        # Generate output filename
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_inverted{ext}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        print(f"Output will be saved to: {output_path}")
        
        # Process PDF
        print("=== Starting PDF processing ===")
        success = invert_pdf_colors(input_path, output_path, PDF_DPI)
        print(f"=== PDF processing result: {success} ===")
        
        if success:
            print("Processing successful, sending file...")
            # Clean up input file
            os.remove(input_path)
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        else:
            print("Processing failed, cleaning up...")
            # Clean up on failure
            if os.path.exists(input_path):
                os.remove(input_path)
            flash('Error processing PDF file - check console logs for details')
            return redirect(url_for('index'))
    else:
        print(f"ERROR: File type not allowed: {file.filename}")
        flash('Please upload a PDF file')
        return redirect(url_for('index'))


if __name__ == '__main__':
    # Use environment variables for host and port in production
    import os
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8002))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)
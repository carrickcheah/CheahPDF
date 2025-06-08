# CheahPDF - PDF Color Inverter

![CheahPDF Interface](screenshot.png)

**Description**: Free local Flask app converts PDF white backgrounds to black backgrounds with white text. Dark mode for PDFs. MIT licensed, runs locally, 1000 DPI output.

A simple Flask web application that converts PDF files from white background to black background with white text at high resolution (1000 DPI).

## Features

- Upload PDF files via web interface
- Convert white backgrounds to black
- Convert black text to white
- High-resolution output at 1000 DPI
- Automatic file download after processing
- Detailed console logging for debugging

## Project Structure

```
cheahpdf/
├── app.py                 # Main Flask application
├── pdf_processor.py       # PDF color inversion logic
├── .env                   # Environment configuration
├── pyproject.toml         # Python project configuration for uv
├── requirements.txt       # Python dependencies (legacy)
├── templates/
│   └── index.html        # Web upload interface
├── uploads/              # Temporary uploaded files (auto-created)
├── outputs/              # Processed PDF files (auto-created)
└── README.md             # This file
```

## Dependencies

- **Flask** - Web framework
- **PyMuPDF (fitz)** - PDF processing library
- **Pillow (PIL)** - Image processing for color inversion
- **python-dotenv** - Environment variable loading

## Installation & Setup

### Using uv (recommended)

```bash
# Install dependencies
uv sync

# Run the application
uv run python app.py
```

### Using pip (alternative)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Configuration

Edit `.env` file to customize settings:

```bash
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
MAX_FILE_SIZE=52428800     # 50MB in bytes
PDF_DPI=1000               # Output resolution
```

## Usage

1. Start the application: `uv run python app.py`
2. Open browser to `http://localhost:8002`
3. Upload a PDF file
4. Wait for processing (console shows progress)
5. Download automatically starts when complete

## How It Works

1. **Upload**: PDF file is uploaded to `uploads/` directory
2. **Processing**: Each page is:
   - Rendered to high-resolution image (1000 DPI)
   - Converted to PIL Image
   - Colors inverted using `ImageOps.invert()`
   - Converted back to PDF page
3. **Output**: Inverted PDF saved to `outputs/` directory
4. **Download**: File sent to user, temporary files cleaned up

## Technical Details

- **Port**: 8002 (avoids macOS Control Center conflicts on 5000)
- **File Limits**: 50MB max upload size
- **Supported Formats**: PDF only
- **Processing**: Synchronous (user waits for completion)
- **Cleanup**: Temporary files automatically removed

## Logging

Detailed console logs show:
- File upload status
- Processing progress per page
- Error details with stack traces
- File sizes and processing times

## Error Handling

- Input validation for file type and size
- Comprehensive error logging
- User-friendly error messages
- Automatic cleanup on failures

## Development

The application uses Flask's debug mode for development:
- Auto-reload on code changes
- Detailed error pages
- Debug console available

## License

MIT License - see LICENSE file for details.
# Use official Python runtime as base image
FROM python:3.11-slim

# Install system dependencies for PyMuPDF and Pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir uv
RUN uv pip install --system flask pymupdf pillow python-dotenv

# Copy application code
COPY . .

# Create temp directories
RUN mkdir -p /tmp/uploads /tmp/outputs

# Expose port
EXPOSE 8002

# Set environment variables for cloud
ENV FLASK_ENV=production
ENV FLASK_DEBUG=False
ENV UPLOAD_FOLDER=/tmp/uploads
ENV OUTPUT_FOLDER=/tmp/outputs
ENV PDF_DPI=300
ENV MAX_FILE_SIZE=10485760

# Run the application
CMD ["python", "app.py"]
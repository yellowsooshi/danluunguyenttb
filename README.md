# Alcohol Label Verification Tool

An AI-powered web application for verifying alcohol beverage labels against regulatory requirements. Upload label images, enter product details, and get instant feedback on label compliance.

## Features

* **Modern Web Interface** - Professional, government-style UI with responsive design
* **Multi-Image Support** - Upload multiple label images (front, back, neck labels) for comprehensive analysis
* **AI-Powered Extraction** - Uses OpenAI's GPT-4 vision model to accurately extract:
  - Brand name
  - Product classification (from 300+ TTB categories)
  - Alcohol by Volume (ABV)
  - Net contents
* **OCR Text Recognition** - Tesseract OCR for initial text extraction from label images
* **Smart Comparison** - Intelligent matching that handles:
  - Unit variations (750ml = 750 milliliters = 750 ML)
  - Case differences
  - Punctuation variations
* **Clear Results** - Color-coded status badges showing match/mismatch/not found for each field
* **TTB Classifications** - Supports 300+ official product classifications

## Requirements

* Python 3.9+
* Tesseract OCR
* OpenAI API key (for AI extraction)

## Quick Start

### 1. Install System Dependencies

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### 2. Clone and Setup

```bash
git clone <repository-url>
cd danluunguyenttb

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Set your OpenAI API key:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

### 4. Run the Application

```bash
python app.py
```

Or using Flask CLI:
```bash
flask run
```

The application will be available at: http://127.0.0.1:5000

## How It Works

1. **Upload Images** - User uploads one or more label images (JPG, PNG, PDF)
2. **OCR Processing** - Tesseract extracts text from each image
3. **AI Analysis** - All images and OCR text sent to OpenAI GPT-4 vision model
4. **Field Extraction** - AI extracts brand, class, ABV, and net contents
5. **Comparison** - Extracted values compared against user input with smart normalization
6. **Report Generation** - Results displayed with clear match/mismatch status

## Project Structure

```
danluunguyenttb/
├── app.py                   # Flask application and routes
├── ai_utils.py             # OpenAI API integration for AI extraction
├── ocr_utils.py            # Tesseract OCR wrapper
├── label_processor.py      # Classification loading and field comparison
├── classifications.json    # TTB product classifications (300+)
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore patterns
├── LICENSE                # License file
└── templates/
    └── index.html         # Web interface template
```

## Dependencies

* **Flask** - Web framework
* **Pillow** - Image processing
* **pytesseract** - OCR text extraction
* **openai** - AI-powered field extraction

## API Costs

The application uses OpenAI's GPT-4 vision model. Costs are minimal for typical usage:
- GPT-4 mini: ~$0.01-0.02 per label verification
- You only pay for what you use

## Deployment

For production deployment, consider:

1. **Platform**: Render, Railway, Fly.io, or Heroku
2. **Environment Variables**: Set `OPENAI_API_KEY` in platform settings
3. **WSGI Server**: Use Gunicorn (included in requirements.txt)
4. **Tesseract**: Ensure Tesseract is available via buildpack or system package

Example Procfile for Heroku:
```
web: gunicorn app:app
```

## Security Notes

* API key is used **server-side only** - never exposed to clients
* Consider adding rate limiting for production use
* File uploads limited to 10MB total
* No data is permanently stored

## Disclaimer

This is an independent third-party tool for label verification and is **not affiliated with, endorsed by, or connected to any government agency**, including the Alcohol and Tobacco Tax and Trade Bureau (TTB) or the U.S. Department of the Treasury. 

This tool is provided for informational purposes only. Always consult official regulatory guidance for compliance requirements.

## License

MIT License - See LICENSE file for details

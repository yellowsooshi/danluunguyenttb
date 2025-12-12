"""Flask web application for alcohol label verification.

Users enter key information about an alcoholic product (brand name, class/type,
ABV and net contents) and upload one or more label images.  The application
extracts text from each label via the OCR utility, parses relevant fields and
compares the results against the submitted form data.  A detailed report is
rendered showing matches, mismatches or missing data.

To run locally:

1. Ensure Python 3.9+ is installed.
2. Install dependencies: ``pip install -r requirements.txt``.
3. Install Tesseract OCR on your system.  On Ubuntu: ``sudo apt-get install
   tesseract-ocr``.  On macOS: ``brew install tesseract``.
4. Start the server: ``flask run`` or ``python app.py``.
5. Navigate to http://localhost:5000/ in your browser.

Deployment guidance is provided in the top‑level README.

"""

from __future__ import annotations

import os
from typing import List, Dict, Optional

from flask import Flask, render_template, request

from ocr_utils import extract_text
from label_processor import CLASSIFICATIONS, compare_fields
from ai_utils import ai_extract_fields



app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Limit uploads to 10MB per request


def process_all_labels(images_data: List[bytes]) -> Dict[str, Optional[str]]:
    """Process all uploaded label images together and return unified extracted data.
    
    This function:
    1. Runs OCR on each image
    2. Combines all OCR text
    3. Passes ALL images and text to AI in one call
    4. AI extracts ALL fields: brand, class_type, abv, net_contents
    
    Parameters
    ----------
    images_data: List[bytes]
        List of image byte data from uploaded files
        
    Returns
    -------
    Dict[str, Optional[str]]
        Dictionary with keys: brand, abv, net_contents, class_type
    """
    if not images_data:
        return {
            "brand": None,
            "abv": None,
            "net_contents": None,
            "class_type": None,
        }
    
    # 1) Run OCR on each image and combine all text
    all_raw_text = []
    for image_data in images_data:
        try:
            raw_text = extract_text(image_data)
            all_raw_text.append(raw_text)
            print(f"OCR extracted ({len(raw_text)} chars)")
        except Exception as e:
            print(f"OCR failed for one image: {e}")
            continue
    
    # Combine all OCR text with separators
    combined_text = "\n---\n".join(all_raw_text)
    
    # 2) Prepare images list as tuples of (bytes, mime_type) for AI
    images_list = [(img_data, "image/png") for img_data in images_data]
    
    # 3) Use AI to extract ALL fields at once
    print(f"Sending {len(images_list)} images to AI for complete extraction...")
    ai_result = ai_extract_fields(combined_text, images=images_list)
    
    if ai_result:
        print(f"AI extracted - Brand: {ai_result.get('brand')}, Class: {ai_result.get('class_type')}, "
              f"ABV: {ai_result.get('abv')}, Net: {ai_result.get('net_contents')}")
        return ai_result
    else:
        print("AI extraction returned None")
        return {
            "brand": None,
            "abv": None,
            "net_contents": None,
            "class_type": None,
        }



@app.route('/', methods=['GET', 'POST'])
def index():
    report: Optional[Dict[str, Dict[str, str]]] = None
    extracted: Optional[Dict[str, Optional[str]]] = None
    error_message: Optional[str] = None
    form_data: Dict[str, str] = {
        "brand": "",
        "class_type": "",
        "abv": "",
        "net_contents": "",
    }
    if request.method == 'POST':
        # Pull form fields
        form_data['brand'] = request.form.get('brand', '')
        form_data['class_type'] = request.form.get('class_type', '')
        form_data['abv'] = request.form.get('abv', '')
        form_data['net_contents'] = request.form.get('net_contents', '')
        
        # Collect all uploaded files
        files = request.files.getlist('labels')
        images_data: List[bytes] = []
        
        for file in files:
            if file and file.filename:
                images_data.append(file.read())
        
        if images_data:
            try:
                # Process ALL images together in one unified call
                extracted = process_all_labels(images_data)
                # Generate ONE unified report
                report = compare_fields(form_data, extracted)
            except RuntimeError as exc:
                # Handle errors gracefully
                error_message = str(exc)
                extracted = {
                    "brand": None,
                    "abv": None,
                    "net_contents": None,
                    "class_type": None,
                }
        else:
            error_message = "No valid image files were uploaded."
    
    return render_template(
        'index.html',
        classifications=CLASSIFICATIONS,
        report=report,
        extracted=extracted,
        error_message=error_message,
        form_data=form_data,
    )


if __name__ == '__main__':  # pragma: no cover
    # Run the development server when executed directly
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

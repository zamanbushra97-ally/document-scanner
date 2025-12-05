"""
Vercel Serverless Function - OCR Processing
Lightweight OCR using Tesseract only (Vercel compatible)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import tempfile
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)

# Import OCR library
try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

def preprocess_image(image_path):
    """Basic image preprocessing"""
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return binary

def extract_metadata(text):
    """Extract basic metadata from text"""
    metadata = {
        "dates": [],
        "emails": [],
        "phone_numbers": [],
        "amounts": []
    }
    
    # Extract dates
    date_patterns = [
        r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
        r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b'
    ]
    for pattern in date_patterns:
        metadata["dates"].extend(re.findall(pattern, text, re.IGNORECASE))
    
    # Extract emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    metadata["emails"] = re.findall(email_pattern, text)
    
    # Extract phone numbers
    phone_pattern = r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    metadata["phone_numbers"] = re.findall(phone_pattern, text)
    
    # Extract amounts
    amount_patterns = [r'₹\s*[\d,]+\.?\d*', r'\$\s*[\d,]+\.?\d*']
    for pattern in amount_patterns:
        metadata["amounts"].extend(re.findall(pattern, text))
    
    return metadata

@app.route('/api/process', methods=['POST', 'OPTIONS'])
def process():
    """Process documents with OCR"""
    if request.method == 'OPTIONS':
        return '', 204
    
    if not TESSERACT_AVAILABLE:
        return jsonify({
            "error": "OCR libraries not available in this environment",
            "suggestion": "Please use local deployment for full OCR capabilities"
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'files' not in data:
            return jsonify({"error": "No files specified"}), 400
        
        results = []
        
        for file_data in data['files']:
            # Decode base64 image
            image_bytes = base64.b64decode(file_data['data'])
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_bytes)
                tmp_path = tmp_file.name
            
            try:
                # Preprocess image
                processed_img = preprocess_image(tmp_path)
                
                # Run OCR
                text = pytesseract.image_to_string(processed_img)
                
                # Get confidence
                data_ocr = pytesseract.image_to_data(processed_img, output_type=pytesseract.Output.DICT)
                confidences = [int(conf) for conf in data_ocr['conf'] if conf != '-1']
                avg_confidence = np.mean(confidences) / 100 if confidences else 0.0
                
                # Extract metadata
                metadata = extract_metadata(text)
                
                result = {
                    "file_name": file_data.get('filename', 'unknown'),
                    "processed_at": datetime.now().isoformat(),
                    "ocr": {
                        "text": text.strip(),
                        "confidence": float(avg_confidence),
                        "engine": "tesseract",
                        "word_count": len(text.split())
                    },
                    "metadata": metadata,
                    "document_type": "unknown"
                }
                
                results.append(result)
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        return jsonify({
            "success": True,
            "results": results,
            "count": len(results)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel serverless handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
MODELS_DIR = BASE_DIR / "backend" / "models"

# Create directories if they don't exist
for directory in [UPLOAD_DIR, OUTPUT_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# OCR Configuration
OCR_CONFIG = {
    "tesseract": {
        "enabled": True,
        "languages": ["eng", "hin", "mar", "ben", "tam", "tel"],  # English, Hindi, Marathi, Bengali, Tamil, Telugu
        "config": "--oem 3 --psm 6",  # LSTM OCR Engine, Assume uniform block of text
    },
    "easyocr": {
        "enabled": True,
        "languages": ["en", "hi", "mr", "bn", "ta", "te"],
        "gpu": True,  # Set to False if no GPU available
    },
    "paddleocr": {
        "enabled": True,
        "lang": "en",
        "use_angle_cls": True,
        "use_gpu": True,  # Set to False if no GPU available
    }
}

# Image Processing Configuration
IMAGE_CONFIG = {
    "dpi": {
        "standard": 300,
        "detailed": 600,
        "archival": 600,
    },
    "formats": {
        "input": [".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".pdf"],
        "output": [".pdf", ".json", ".csv", ".txt"],
    },
    "preprocessing": {
        "denoise": True,
        "deskew": True,
        "enhance_contrast": True,
        "remove_shadows": True,
    }
}

# Document Classification
DOCUMENT_TYPES = [
    "handwritten",
    "printed",
    "mixed",
    "form",
    "invoice",
    "letter",
    "manuscript",
    "gazette",
    "legal",
    "administrative"
]

# Output Formats
OUTPUT_FORMATS = {
    "pdf_a": True,  # PDF/A for archival
    "searchable_pdf": True,  # PDF with OCR text layer
    "json": True,  # Structured JSON output
    "csv": True,  # Metadata CSV
    "txt": True,  # Plain text
}

# API Configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": True,
    "max_upload_size": 50 * 1024 * 1024,  # 50 MB
    "allowed_extensions": {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".pdf"},
}

# NER Configuration
NER_CONFIG = {
    "enabled": True,
    "entities": ["PERSON", "ORG", "DATE", "GPE", "MONEY", "CARDINAL"],
    "model": "en_core_web_sm",  # spaCy model
}

# Confidence Thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.9,
    "medium": 0.7,
    "low": 0.5,
}

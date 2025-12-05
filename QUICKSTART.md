# Quick Start Guide

## Prerequisites

Before running the Document Scanner, ensure you have:

1. **Python 3.8+** installed
2. **Tesseract OCR** installed on your system

## Step-by-Step Setup

### 1. Install Tesseract OCR

#### Windows
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer
3. Add Tesseract to your PATH:
   - Right-click "This PC" → Properties → Advanced System Settings
   - Environment Variables → System Variables → Path → Edit
   - Add: `C:\Program Files\Tesseract-OCR`

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-hin  # For Hindi support
```

#### macOS
```bash
brew install tesseract
brew install tesseract-lang  # For additional languages
```

### 2. Install Python Dependencies

Open terminal/command prompt in the project directory:

```bash
cd d:\SCANNER

# Install all required packages
pip install -r requirements.txt

# Download spaCy language model for NER
python -m spacy download en_core_web_sm
```

**Note**: This may take 5-10 minutes as it downloads deep learning models for EasyOCR and PaddleOCR.

### 3. Verify Installation

Run the test script to check if everything is working:

```bash
python test_scanner.py
```

You should see:
- ✓ Image Preprocessing: PASSED
- ✓ OCR Engines: PASSED  
- ✓ Full Pipeline: PASSED

### 4. Start the Server

```bash
python backend/api_server.py
```

You should see:
```
Starting Document Scanner API Server...
Upload directory: d:\SCANNER\uploads
Output directory: d:\SCANNER\output
 * Running on http://0.0.0.0:5000
```

### 5. Open the Web Interface

Open your browser and go to:
```
http://localhost:5000
```

## Using the Application

### Upload Documents

1. **Drag and drop** files onto the upload area, or
2. **Click** the upload area to browse files
3. Supported formats: JPG, PNG, TIFF, PDF

### Process Documents

1. Click **"Process Documents"** button
2. Wait for processing (progress bar shows status)
3. View results with extracted text and metadata

### View Details

- Click any result card to see full document details
- View extracted text, metadata, and tags
- Check confidence scores and OCR engine used

### Export Results

- **Export JSON**: Download all results as structured JSON
- **Export CSV**: Download metadata as CSV spreadsheet

## Troubleshooting

### "Tesseract not found"

**Solution**: Make sure Tesseract is installed and in your PATH.

If still not working, edit `backend/scanner_engine.py` and add:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### "Module not found" errors

**Solution**: Install missing dependencies:
```bash
pip install -r requirements.txt
```

### Low OCR accuracy

**Solutions**:
- Use higher quality scans (300+ DPI)
- Ensure good lighting and contrast
- Enable all preprocessing options
- Try different OCR engines

### Out of memory

**Solutions**:
- Process fewer documents at once
- Reduce image resolution
- Disable GPU in `config.py` if causing issues

### Server won't start

**Solutions**:
- Check if port 5000 is already in use
- Try a different port in `backend/config.py`
- Check firewall settings

## Sample Test Documents

Two sample documents are included in the `uploads/` folder:
1. `sample_handwritten_document.png` - Handwritten letter
2. `sample_printed_document.png` - Printed invoice

Use these to test the system!

## Next Steps

1. **Add your own documents** to the `uploads/` folder
2. **Customize settings** in `backend/config.py`
3. **Explore the API** at `http://localhost:5000/api/`
4. **Check the README** for advanced features

## Support

For detailed documentation, see:
- `README.md` - Full documentation
- `walkthrough.md` - Feature walkthrough
- `implementation_plan.md` - Technical details

---

**Happy scanning!** 📄✨

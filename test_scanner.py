"""
Simple test script to verify OCR functionality
Run this to test the scanner with a sample image
"""

import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.scanner_engine import MultiEngineOCR
from backend.document_processor import DocumentProcessor
from backend.utils.image_utils import ImagePreprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_image_preprocessing():
    """Test image preprocessing utilities"""
    print("\n" + "="*50)
    print("Testing Image Preprocessing")
    print("="*50)
    
    preprocessor = ImagePreprocessor()
    
    # Test with a sample image if available
    sample_images = list(Path("uploads").glob("*.[jp][pn]g"))
    
    if not sample_images:
        print("❌ No sample images found in uploads/ directory")
        print("   Please add some test images to the uploads/ folder")
        return False
    
    test_image = str(sample_images[0])
    print(f"✓ Testing with: {Path(test_image).name}")
    
    try:
        # Test quality assessment
        import cv2
        img = cv2.imread(test_image)
        quality = preprocessor.assess_quality(img)
        print(f"✓ Quality assessment: {quality['quality']}")
        print(f"  - Sharpness: {quality['sharpness']:.2f}")
        print(f"  - Brightness: {quality['brightness']:.2f}")
        print(f"  - Contrast: {quality['contrast']:.2f}")
        
        # Test document type detection
        doc_type = preprocessor.detect_document_type(img)
        print(f"✓ Document type: {doc_type}")
        
        return True
    except Exception as e:
        print(f"❌ Preprocessing test failed: {e}")
        return False

def test_ocr_engines():
    """Test OCR engine initialization"""
    print("\n" + "="*50)
    print("Testing OCR Engines")
    print("="*50)
    
    try:
        ocr = MultiEngineOCR()
        print(f"✓ Initialized {len(ocr.engines)} OCR engine(s):")
        for name, info in ocr.engines.items():
            print(f"  - {info['name']}: best for {info['best_for']} text")
        return True
    except Exception as e:
        print(f"❌ OCR initialization failed: {e}")
        print("\nMake sure you have installed:")
        print("  - Tesseract OCR")
        print("  - pip install pytesseract easyocr paddleocr")
        return False

def test_full_pipeline():
    """Test complete document processing pipeline"""
    print("\n" + "="*50)
    print("Testing Full Processing Pipeline")
    print("="*50)
    
    # Find a test image
    sample_images = list(Path("uploads").glob("*.[jp][pn]g"))
    
    if not sample_images:
        print("❌ No sample images found")
        return False
    
    test_image = str(sample_images[0])
    print(f"✓ Processing: {Path(test_image).name}")
    
    try:
        processor = DocumentProcessor()
        result = processor.process_document(test_image, output_formats=['json', 'txt'])
        
        print(f"\n✓ Processing complete!")
        print(f"  - Extracted text length: {len(result['ocr']['text'])} characters")
        print(f"  - Confidence: {result['ocr']['confidence']*100:.1f}%")
        print(f"  - Word count: {result['ocr']['word_count']}")
        print(f"  - Document type: {result['document_type']}")
        print(f"  - Engine used: {result['ocr']['engine']}")
        
        # Show metadata
        metadata = result['metadata']
        if metadata.get('dates'):
            print(f"  - Dates found: {', '.join(metadata['dates'][:3])}")
        if metadata.get('names'):
            print(f"  - Names found: {', '.join(metadata['names'][:3])}")
        
        # Show preview of text
        text_preview = result['ocr']['text'][:200]
        print(f"\n📄 Text Preview:")
        print(f"  {text_preview}...")
        
        return True
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  DOCUMENT SCANNER - SYSTEM TEST")
    print("="*60)
    
    results = {
        "Image Preprocessing": test_image_preprocessing(),
        "OCR Engines": test_ocr_engines(),
        "Full Pipeline": test_full_pipeline(),
    }
    
    print("\n" + "="*60)
    print("  TEST RESULTS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! System is ready.")
        print("\nNext steps:")
        print("  1. Run: python backend/api_server.py")
        print("  2. Open: http://localhost:5000")
        print("  3. Upload and process documents!")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("  - Install Tesseract OCR")
        print("  - Run: pip install -r requirements.txt")
        print("  - Add test images to uploads/ folder")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

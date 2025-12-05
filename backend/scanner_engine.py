"""
Multi-engine OCR Scanner
Combines Tesseract, EasyOCR, and PaddleOCR for optimal text extraction
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

# OCR Engines
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("Tesseract not available")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logging.warning("EasyOCR not available")

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    logging.warning("PaddleOCR not available")

from backend.utils.image_utils import ImagePreprocessor
from backend.config import OCR_CONFIG, CONFIDENCE_THRESHOLDS

logger = logging.getLogger(__name__)


class MultiEngineOCR:
    """
    Hybrid OCR engine that combines multiple OCR systems
    for optimal accuracy across different document types
    """
    
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.engines = {}
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize available OCR engines"""
        logger.info("Initializing OCR engines...")
        
        # Initialize Tesseract
        if TESSERACT_AVAILABLE and OCR_CONFIG["tesseract"]["enabled"]:
            self.engines["tesseract"] = {
                "name": "Tesseract",
                "available": True,
                "best_for": "printed",
            }
            logger.info("✓ Tesseract OCR initialized")
        
        # Initialize EasyOCR
        if EASYOCR_AVAILABLE and OCR_CONFIG["easyocr"]["enabled"]:
            try:
                self.easyocr_reader = easyocr.Reader(
                    OCR_CONFIG["easyocr"]["languages"],
                    gpu=OCR_CONFIG["easyocr"]["gpu"]
                )
                self.engines["easyocr"] = {
                    "name": "EasyOCR",
                    "available": True,
                    "best_for": "handwritten",
                }
                logger.info("✓ EasyOCR initialized")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
        
        # Initialize PaddleOCR
        if PADDLEOCR_AVAILABLE and OCR_CONFIG["paddleocr"]["enabled"]:
            try:
                self.paddleocr_reader = PaddleOCR(
                    use_angle_cls=OCR_CONFIG["paddleocr"]["use_angle_cls"],
                    lang=OCR_CONFIG["paddleocr"]["lang"],
                    use_gpu=OCR_CONFIG["paddleocr"]["use_gpu"],
                    show_log=False
                )
                self.engines["paddle"] = {
                    "name": "PaddleOCR",
                    "available": True,
                    "best_for": "mixed",
                }
                logger.info("✓ PaddleOCR initialized")
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR: {e}")
        
        if not self.engines:
            raise RuntimeError("No OCR engines available! Please install at least one OCR library.")
        
        logger.info(f"Initialized {len(self.engines)} OCR engine(s)")
    
    def extract_text(
        self,
        image_path: str,
        document_type: Optional[str] = None,
        preprocess: bool = True
    ) -> Dict:
        """
        Extract text from image using the best OCR engine
        
        Args:
            image_path: Path to image file
            document_type: Type of document ("printed", "handwritten", "mixed")
            preprocess: Whether to preprocess image
        
        Returns:
            Dict with extracted text, confidence, and metadata
        """
        logger.info(f"Processing: {image_path}")
        
        # Load and preprocess image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        if preprocess:
            image = self.preprocessor.preprocess(image_path)
        
        # Detect document type if not provided
        if document_type is None:
            document_type = self.preprocessor.detect_document_type(image)
            logger.info(f"Detected document type: {document_type}")
        
        # Assess image quality
        quality_metrics = self.preprocessor.assess_quality(image)
        logger.info(f"Image quality: {quality_metrics['quality']}")
        
        # Select best engine based on document type
        engine = self._select_engine(document_type)
        logger.info(f"Using OCR engine: {engine}")
        
        # Extract text using selected engine
        if engine == "tesseract":
            result = self._ocr_tesseract(image)
        elif engine == "easyocr":
            result = self._ocr_easyocr(image)
        elif engine == "paddle":
            result = self._ocr_paddle(image)
        else:
            # Fallback: try all available engines
            result = self._ocr_ensemble(image)
        
        # Add metadata
        result["document_type"] = document_type
        result["quality_metrics"] = quality_metrics
        result["engine_used"] = engine
        result["image_path"] = image_path
        
        return result
    
    def _select_engine(self, document_type: str) -> str:
        """Select best OCR engine based on document type"""
        
        # Priority mapping
        priority = {
            "printed": ["tesseract", "paddle", "easyocr"],
            "handwritten": ["easyocr", "paddle", "tesseract"],
            "mixed": ["paddle", "easyocr", "tesseract"],
            "unknown": ["tesseract", "paddle", "easyocr"],
        }
        
        # Get priority list for document type
        engine_priority = priority.get(document_type, priority["unknown"])
        
        # Return first available engine
        for engine in engine_priority:
            if engine in self.engines:
                return engine
        
        # Fallback to any available engine
        return list(self.engines.keys())[0]
    
    def _ocr_tesseract(self, image: np.ndarray) -> Dict:
        """Extract text using Tesseract OCR"""
        logger.debug("Running Tesseract OCR...")
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Get OCR configuration
        config = OCR_CONFIG["tesseract"]["config"]
        
        # Extract text
        text = pytesseract.image_to_string(gray, config=config)
        
        # Get detailed data for confidence
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT, config=config)
        
        # Calculate average confidence
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        avg_confidence = np.mean(confidences) / 100 if confidences else 0.0
        
        return {
            "text": text.strip(),
            "confidence": float(avg_confidence),
            "engine": "tesseract",
            "word_count": len(text.split()),
            "details": data,
        }
    
    def _ocr_easyocr(self, image: np.ndarray) -> Dict:
        """Extract text using EasyOCR"""
        logger.debug("Running EasyOCR...")
        
        # EasyOCR expects RGB
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Extract text
        results = self.easyocr_reader.readtext(image)
        
        # Combine all text
        text_parts = []
        confidences = []
        
        for (bbox, text, conf) in results:
            text_parts.append(text)
            confidences.append(conf)
        
        full_text = " ".join(text_parts)
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        return {
            "text": full_text.strip(),
            "confidence": float(avg_confidence),
            "engine": "easyocr",
            "word_count": len(full_text.split()),
            "details": results,
        }
    
    def _ocr_paddle(self, image: np.ndarray) -> Dict:
        """Extract text using PaddleOCR"""
        logger.debug("Running PaddleOCR...")
        
        # PaddleOCR expects BGR
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # Extract text
        results = self.paddleocr_reader.ocr(image, cls=True)
        
        # Combine all text
        text_parts = []
        confidences = []
        
        if results and results[0]:
            for line in results[0]:
                if line:
                    text = line[1][0]
                    conf = line[1][1]
                    text_parts.append(text)
                    confidences.append(conf)
        
        full_text = " ".join(text_parts)
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        return {
            "text": full_text.strip(),
            "confidence": float(avg_confidence),
            "engine": "paddle",
            "word_count": len(full_text.split()),
            "details": results,
        }
    
    def _ocr_ensemble(self, image: np.ndarray) -> Dict:
        """
        Run multiple OCR engines and combine results
        using confidence-weighted voting
        """
        logger.debug("Running ensemble OCR...")
        
        results = []
        
        # Run all available engines
        if "tesseract" in self.engines:
            results.append(self._ocr_tesseract(image))
        
        if "easyocr" in self.engines:
            results.append(self._ocr_easyocr(image))
        
        if "paddle" in self.engines:
            results.append(self._ocr_paddle(image))
        
        if not results:
            return {
                "text": "",
                "confidence": 0.0,
                "engine": "none",
                "word_count": 0,
            }
        
        # Select result with highest confidence
        best_result = max(results, key=lambda x: x["confidence"])
        best_result["engine"] = f"ensemble ({best_result['engine']} selected)"
        best_result["all_results"] = results
        
        return best_result
    
    def batch_extract(self, image_paths: List[str], **kwargs) -> List[Dict]:
        """
        Extract text from multiple images
        
        Args:
            image_paths: List of image file paths
            **kwargs: Additional arguments for extract_text
        
        Returns:
            List of extraction results
        """
        logger.info(f"Batch processing {len(image_paths)} images...")
        
        results = []
        for i, path in enumerate(image_paths, 1):
            logger.info(f"Processing {i}/{len(image_paths)}: {Path(path).name}")
            try:
                result = self.extract_text(path, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {path}: {e}")
                results.append({
                    "text": "",
                    "confidence": 0.0,
                    "error": str(e),
                    "image_path": path,
                })
        
        logger.info(f"Batch processing complete: {len(results)} results")
        return results

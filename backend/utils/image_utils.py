"""
Image preprocessing utilities for document scanning
Includes de-skewing, de-noising, contrast enhancement, and quality assessment
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Handles all image preprocessing operations"""
    
    def __init__(self):
        self.processed_images = []
    
    def preprocess(self, image_path: str, operations: dict = None) -> np.ndarray:
        """
        Main preprocessing pipeline
        
        Args:
            image_path: Path to the image file
            operations: Dict of operations to perform (default: all)
        
        Returns:
            Preprocessed image as numpy array
        """
        if operations is None:
            operations = {
                "denoise": True,
                "deskew": True,
                "enhance_contrast": True,
                "remove_shadows": True,
            }
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        logger.info(f"Preprocessing image: {image_path}")
        
        # Apply operations in sequence
        if operations.get("denoise", False):
            img = self.denoise(img)
        
        if operations.get("deskew", False):
            img = self.deskew(img)
        
        if operations.get("remove_shadows", False):
            img = self.remove_shadows(img)
        
        if operations.get("enhance_contrast", False):
            img = self.enhance_contrast(img)
        
        return img
    
    def denoise(self, image: np.ndarray) -> np.ndarray:
        """Remove noise from image using Non-local Means Denoising"""
        logger.debug("Applying denoising...")
        
        # Convert to grayscale if color
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            # Convert back to BGR
            return cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)
        else:
            return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
    
    def deskew(self, image: np.ndarray) -> np.ndarray:
        """Correct skew/rotation in scanned documents"""
        logger.debug("Applying deskew...")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Apply threshold to get binary image
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        # Find all non-zero points
        coords = np.column_stack(np.where(thresh > 0))
        
        if len(coords) == 0:
            return image
        
        # Calculate rotation angle
        angle = cv2.minAreaRect(coords)[-1]
        
        # Adjust angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Only rotate if angle is significant (> 0.5 degrees)
        if abs(angle) < 0.5:
            return image
        
        # Rotate image
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        logger.debug(f"Corrected skew angle: {angle:.2f} degrees")
        return rotated
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)"""
        logger.debug("Enhancing contrast...")
        
        # Convert to LAB color space
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
        else:
            l = image
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels and convert back
        if len(image.shape) == 3:
            lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            enhanced = l
        
        return enhanced
    
    def remove_shadows(self, image: np.ndarray) -> np.ndarray:
        """Remove shadows and uneven illumination"""
        logger.debug("Removing shadows...")
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Dilate image to remove text
        dilated = cv2.dilate(gray, np.ones((7, 7), np.uint8))
        
        # Blur to get background
        bg = cv2.medianBlur(dilated, 21)
        
        # Calculate difference
        diff = 255 - cv2.absdiff(gray, bg)
        
        # Normalize
        norm = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        
        # Convert back to BGR if needed
        if len(image.shape) == 3:
            return cv2.cvtColor(norm, cv2.COLOR_GRAY2BGR)
        
        return norm
    
    def assess_quality(self, image: np.ndarray) -> dict:
        """
        Assess image quality for OCR
        
        Returns:
            Dict with quality metrics
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Calculate sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate brightness
        brightness = np.mean(gray)
        
        # Calculate contrast
        contrast = gray.std()
        
        # Determine quality level
        quality = "good"
        if laplacian_var < 100:
            quality = "blurry"
        elif brightness < 50 or brightness > 200:
            quality = "poor_lighting"
        elif contrast < 30:
            quality = "low_contrast"
        
        return {
            "sharpness": float(laplacian_var),
            "brightness": float(brightness),
            "contrast": float(contrast),
            "quality": quality,
            "resolution": image.shape[:2],
        }
    
    def detect_document_type(self, image: np.ndarray) -> str:
        """
        Detect if document is handwritten or printed
        
        Returns:
            "handwritten", "printed", or "mixed"
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return "unknown"
        
        # Analyze contour characteristics
        areas = [cv2.contourArea(c) for c in contours]
        perimeters = [cv2.arcLength(c, True) for c in contours]
        
        # Calculate complexity (perimeter^2 / area)
        complexities = [p*p / (a + 1) for p, a in zip(perimeters, areas) if a > 10]
        
        if not complexities:
            return "unknown"
        
        avg_complexity = np.mean(complexities)
        
        # Heuristic: handwritten text tends to have higher complexity
        if avg_complexity > 100:
            return "handwritten"
        elif avg_complexity > 50:
            return "mixed"
        else:
            return "printed"
    
    def save_image(self, image: np.ndarray, output_path: str) -> None:
        """Save processed image"""
        cv2.imwrite(output_path, image)
        logger.info(f"Saved processed image to: {output_path}")


def resize_for_ocr(image: np.ndarray, target_dpi: int = 300) -> np.ndarray:
    """
    Resize image to optimal DPI for OCR
    
    Args:
        image: Input image
        target_dpi: Target DPI (default 300)
    
    Returns:
        Resized image
    """
    # Assume input is 72 DPI (screen resolution)
    scale_factor = target_dpi / 72
    
    if scale_factor == 1.0:
        return image
    
    width = int(image.shape[1] * scale_factor)
    height = int(image.shape[0] * scale_factor)
    
    resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)
    return resized

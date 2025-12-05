"""
Document processor - combines OCR, metadata extraction, and output generation
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

from backend.scanner_engine import MultiEngineOCR
from backend.utils.metadata_extractor import MetadataExtractor
from backend.config import OUTPUT_DIR

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Main document processing pipeline"""
    
    def __init__(self):
        self.ocr_engine = MultiEngineOCR()
        self.metadata_extractor = MetadataExtractor()
        self.processed_documents = []
    
    def process_document(
        self,
        image_path: str,
        output_formats: Optional[List[str]] = None
    ) -> Dict:
        """
        Process a single document through the complete pipeline
        
        Args:
            image_path: Path to image file
            output_formats: List of output formats to generate
        
        Returns:
            Processing result with all extracted data
        """
        logger.info(f"Processing document: {image_path}")
        
        # Step 1: OCR extraction
        ocr_result = self.ocr_engine.extract_text(image_path, preprocess=True)
        
        # Step 2: Metadata extraction
        metadata = self.metadata_extractor.extract_all(ocr_result["text"])
        
        # Step 3: Generate tags
        tags = self.metadata_extractor.generate_tags(ocr_result["text"], metadata)
        
        # Combine all results
        result = {
            "file_name": Path(image_path).name,
            "file_path": image_path,
            "processed_at": datetime.now().isoformat(),
            "ocr": {
                "text": ocr_result["text"],
                "confidence": ocr_result["confidence"],
                "engine": ocr_result["engine"],
                "word_count": ocr_result["word_count"],
            },
            "metadata": metadata,
            "tags": tags,
            "document_type": ocr_result.get("document_type", "unknown"),
            "quality_metrics": ocr_result.get("quality_metrics", {}),
        }
        
        # Store result
        self.processed_documents.append(result)
        
        # Generate output files
        if output_formats:
            self._generate_outputs(result, output_formats)
        
        logger.info(f"✓ Document processed successfully: {Path(image_path).name}")
        return result
    
    def process_batch(
        self,
        image_paths: List[str],
        output_formats: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Process multiple documents
        
        Args:
            image_paths: List of image file paths
            output_formats: List of output formats to generate
        
        Returns:
            List of processing results
        """
        logger.info(f"Batch processing {len(image_paths)} documents...")
        
        results = []
        for i, path in enumerate(image_paths, 1):
            logger.info(f"Processing {i}/{len(image_paths)}")
            try:
                result = self.process_document(path, output_formats)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {path}: {e}")
                results.append({
                    "file_name": Path(path).name,
                    "file_path": path,
                    "error": str(e),
                    "processed_at": datetime.now().isoformat(),
                })
        
        logger.info(f"✓ Batch processing complete: {len(results)} documents")
        return results
    
    def _generate_outputs(self, result: Dict, formats: List[str]) -> None:
        """Generate output files in specified formats"""
        
        output_base = OUTPUT_DIR / Path(result["file_name"]).stem
        
        if "json" in formats:
            self._save_json(result, f"{output_base}.json")
        
        if "txt" in formats:
            self._save_txt(result, f"{output_base}.txt")
        
        if "csv" in formats:
            self._save_csv([result], f"{output_base}.csv")
    
    def _save_json(self, result: Dict, output_path: str) -> None:
        """Save result as JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON: {output_path}")
    
    def _save_txt(self, result: Dict, output_path: str) -> None:
        """Save extracted text as TXT"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result["ocr"]["text"])
        logger.info(f"Saved TXT: {output_path}")
    
    def _save_csv(self, results: List[Dict], output_path: str) -> None:
        """Save metadata as CSV"""
        if not results:
            return
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                "file_name",
                "processed_at",
                "document_type",
                "confidence",
                "word_count",
                "dates",
                "names",
                "organizations",
                "locations",
                "tags",
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                if "error" in result:
                    continue
                
                row = {
                    "file_name": result["file_name"],
                    "processed_at": result["processed_at"],
                    "document_type": result["document_type"],
                    "confidence": result["ocr"]["confidence"],
                    "word_count": result["ocr"]["word_count"],
                    "dates": "; ".join(result["metadata"].get("dates", [])),
                    "names": "; ".join(result["metadata"].get("names", [])),
                    "organizations": "; ".join(result["metadata"].get("organizations", [])),
                    "locations": "; ".join(result["metadata"].get("locations", [])),
                    "tags": "; ".join(result["tags"]),
                }
                writer.writerow(row)
        
        logger.info(f"Saved CSV: {output_path}")
    
    def export_all_metadata(self, output_path: str = None) -> None:
        """Export metadata for all processed documents to CSV"""
        if not self.processed_documents:
            logger.warning("No documents to export")
            return
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = OUTPUT_DIR / f"metadata_export_{timestamp}.csv"
        
        self._save_csv(self.processed_documents, output_path)
        logger.info(f"Exported metadata for {len(self.processed_documents)} documents")
    
    def search_documents(self, query: str) -> List[Dict]:
        """
        Search processed documents by text content or metadata
        
        Args:
            query: Search query
        
        Returns:
            List of matching documents
        """
        query_lower = query.lower()
        results = []
        
        for doc in self.processed_documents:
            # Search in text
            if query_lower in doc["ocr"]["text"].lower():
                results.append(doc)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in doc["tags"]):
                results.append(doc)
                continue
            
            # Search in metadata
            metadata = doc["metadata"]
            for key, values in metadata.items():
                if isinstance(values, list):
                    if any(query_lower in str(v).lower() for v in values):
                        results.append(doc)
                        break
        
        logger.info(f"Search '{query}': found {len(results)} results")
        return results
    
    def get_statistics(self) -> Dict:
        """Get processing statistics"""
        if not self.processed_documents:
            return {}
        
        total_docs = len(self.processed_documents)
        total_words = sum(doc["ocr"]["word_count"] for doc in self.processed_documents if "error" not in doc)
        avg_confidence = sum(doc["ocr"]["confidence"] for doc in self.processed_documents if "error" not in doc) / total_docs
        
        # Document type distribution
        doc_types = {}
        for doc in self.processed_documents:
            if "error" not in doc:
                doc_type = doc["document_type"]
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        return {
            "total_documents": total_docs,
            "total_words": total_words,
            "average_confidence": round(avg_confidence, 2),
            "document_types": doc_types,
        }

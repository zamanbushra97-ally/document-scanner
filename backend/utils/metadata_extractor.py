"""
Metadata extraction utilities using NLP and pattern matching
Extracts dates, names, document types, and other key information
"""

import re
from datetime import datetime
from typing import Dict, List, Optional
import logging

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available")

from backend.config import NER_CONFIG

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extract metadata from OCR text"""
    
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE and NER_CONFIG["enabled"]:
            try:
                self.nlp = spacy.load(NER_CONFIG["model"])
                logger.info("✓ spaCy NER model loaded")
            except Exception as e:
                logger.warning(f"Could not load spaCy model: {e}")
                logger.info("Run: python -m spacy download en_core_web_sm")
    
    def extract_all(self, text: str) -> Dict:
        """
        Extract all metadata from text
        
        Args:
            text: OCR extracted text
        
        Returns:
            Dict with all extracted metadata
        """
        metadata = {
            "dates": self.extract_dates(text),
            "names": self.extract_names(text),
            "organizations": self.extract_organizations(text),
            "locations": self.extract_locations(text),
            "emails": self.extract_emails(text),
            "phone_numbers": self.extract_phone_numbers(text),
            "reference_numbers": self.extract_reference_numbers(text),
            "amounts": self.extract_amounts(text),
            "document_type": self.classify_document_type(text),
        }
        
        return metadata
    
    def extract_dates(self, text: str) -> List[str]:
        """Extract dates in various formats"""
        dates = []
        
        # Common date patterns
        patterns = [
            r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',  # DD/MM/YYYY or MM/DD/YYYY
            r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',  # YYYY/MM/DD
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b',  # DD Month YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}\b',  # Month DD, YYYY
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        # Use NER if available
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "DATE":
                    dates.append(ent.text)
        
        return list(set(dates))  # Remove duplicates
    
    def extract_names(self, text: str) -> List[str]:
        """Extract person names using NER"""
        names = []
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    names.append(ent.text)
        else:
            # Fallback: simple pattern matching for capitalized words
            pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
            matches = re.findall(pattern, text)
            names.extend(matches)
        
        return list(set(names))
    
    def extract_organizations(self, text: str) -> List[str]:
        """Extract organization names using NER"""
        orgs = []
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    orgs.append(ent.text)
        
        return list(set(orgs))
    
    def extract_locations(self, text: str) -> List[str]:
        """Extract location names using NER"""
        locations = []
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["GPE", "LOC"]:
                    locations.append(ent.text)
        
        return list(set(locations))
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)
        return list(set(emails))
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers (Indian and international formats)"""
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # International
            r'\b\d{10}\b',  # 10-digit Indian
            r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',  # XXX-XXX-XXXX
        ]
        
        phone_numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            phone_numbers.extend(matches)
        
        return list(set(phone_numbers))
    
    def extract_reference_numbers(self, text: str) -> List[str]:
        """Extract reference/document numbers"""
        patterns = [
            r'\b[A-Z]{2,}\d{4,}\b',  # ABC1234
            r'\b\d{4,}[A-Z]{2,}\b',  # 1234ABC
            r'\bRef\.?\s*No\.?\s*:?\s*([A-Z0-9/-]+)\b',  # Ref No: XXX
            r'\bDoc\.?\s*No\.?\s*:?\s*([A-Z0-9/-]+)\b',  # Doc No: XXX
        ]
        
        ref_numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            ref_numbers.extend(matches)
        
        return list(set(ref_numbers))
    
    def extract_amounts(self, text: str) -> List[str]:
        """Extract monetary amounts"""
        patterns = [
            r'₹\s*[\d,]+\.?\d*',  # Rupees
            r'Rs\.?\s*[\d,]+\.?\d*',  # Rs.
            r'\$\s*[\d,]+\.?\d*',  # Dollars
            r'\b[\d,]+\.?\d*\s*(?:rupees|dollars|euros)\b',  # Written currency
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            amounts.extend(matches)
        
        # Use NER if available
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "MONEY":
                    amounts.append(ent.text)
        
        return list(set(amounts))
    
    def classify_document_type(self, text: str) -> str:
        """
        Classify document type based on content
        
        Returns:
            Document type classification
        """
        text_lower = text.lower()
        
        # Define keywords for each document type
        type_keywords = {
            "invoice": ["invoice", "bill", "amount due", "total amount", "payment"],
            "letter": ["dear", "sincerely", "regards", "yours truly"],
            "form": ["form", "application", "fill", "signature"],
            "legal": ["agreement", "contract", "hereby", "whereas", "party"],
            "gazette": ["notification", "gazette", "government order"],
            "manuscript": ["chapter", "page", "manuscript"],
            "administrative": ["memo", "memorandum", "circular", "office order"],
            "receipt": ["receipt", "received", "paid"],
        }
        
        # Count keyword matches
        scores = {}
        for doc_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[doc_type] = score
        
        # Return type with highest score
        if scores:
            return max(scores, key=scores.get)
        
        return "unknown"
    
    def generate_tags(self, text: str, metadata: Optional[Dict] = None) -> List[str]:
        """
        Generate searchable tags from text and metadata
        
        Args:
            text: OCR text
            metadata: Optional metadata dict
        
        Returns:
            List of tags
        """
        tags = []
        
        if metadata is None:
            metadata = self.extract_all(text)
        
        # Add document type
        if metadata.get("document_type"):
            tags.append(metadata["document_type"])
        
        # Add organizations
        tags.extend(metadata.get("organizations", []))
        
        # Add locations
        tags.extend(metadata.get("locations", []))
        
        # Extract key terms (most common meaningful words)
        words = text.lower().split()
        # Filter out common words
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        meaningful_words = [w for w in words if len(w) > 3 and w not in stopwords]
        
        # Count word frequency
        from collections import Counter
        word_freq = Counter(meaningful_words)
        
        # Add top 5 most common words as tags
        top_words = [word for word, count in word_freq.most_common(5)]
        tags.extend(top_words)
        
        return list(set(tags))  # Remove duplicates

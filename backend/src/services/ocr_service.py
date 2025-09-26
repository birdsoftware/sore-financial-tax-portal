import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import tempfile
import re
from typing import Dict, List, Optional

class OCRService:
    """Service for extracting text and data from tax documents using OCR."""
    
    def __init__(self):
        # Configure tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        pass
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image file."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        try:
            # Convert PDF to images
            pages = convert_from_path(pdf_path)
            extracted_text = ""
            
            for page in pages:
                # Extract text from each page
                text = pytesseract.image_to_string(page)
                extracted_text += text + "\n"
            
            return extracted_text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_document(self, file_path: str) -> str:
        """Extract text from a document (PDF or image)."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
            return self.extract_text_from_image(file_path)
        else:
            return ""
    
    def extract_w2_data(self, text: str) -> Dict:
        """Extract structured data from W-2 form text."""
        data = {}
        
        # Common W-2 patterns
        patterns = {
            'employer_name': r'(?:employer|company)[:\s]*([A-Za-z\s&,.-]+?)(?:\n|$)',
            'employee_name': r'(?:employee|name)[:\s]*([A-Za-z\s,.-]+?)(?:\n|$)',
            'wages': r'(?:wages|box\s*1)[:\s]*\$?([0-9,]+\.?[0-9]*)',
            'federal_tax': r'(?:federal.*tax|box\s*2)[:\s]*\$?([0-9,]+\.?[0-9]*)',
            'social_security_wages': r'(?:social.*security.*wages|box\s*3)[:\s]*\$?([0-9,]+\.?[0-9]*)',
            'medicare_wages': r'(?:medicare.*wages|box\s*5)[:\s]*\$?([0-9,]+\.?[0-9]*)',
            'ein': r'(?:ein|employer.*id)[:\s]*([0-9-]+)',
            'ssn': r'(?:ssn|social.*security)[:\s]*([0-9-]+)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data[field] = match.group(1).strip()
        
        return data
    
    def extract_1099_data(self, text: str) -> Dict:
        """Extract structured data from 1099 form text."""
        data = {}
        
        # Common 1099 patterns
        patterns = {
            'payer_name': r'(?:payer|company)[:\s]*([A-Za-z\s&,.-]+?)(?:\n|$)',
            'recipient_name': r'(?:recipient|payee)[:\s]*([A-Za-z\s,.-]+?)(?:\n|$)',
            'nonemployee_compensation': r'(?:nonemployee.*compensation|box\s*1)[:\s]*\$?([0-9,]+\.?[0-9]*)',
            'federal_tax': r'(?:federal.*tax|box\s*4)[:\s]*\$?([0-9,]+\.?[0-9]*)',
            'payer_tin': r'(?:payer.*tin|ein)[:\s]*([0-9-]+)',
            'recipient_tin': r'(?:recipient.*tin|ssn)[:\s]*([0-9-]+)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data[field] = match.group(1).strip()
        
        return data
    
    def extract_receipt_data(self, text: str) -> Dict:
        """Extract structured data from receipt text."""
        data = {}
        
        # Receipt patterns
        patterns = {
            'merchant_name': r'^([A-Za-z\s&,.-]+?)(?:\n|$)',
            'total_amount': r'(?:total|amount)[:\s]*\$?([0-9,]+\.?[0-9]*)',
            'date': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'tax_amount': r'(?:tax)[:\s]*\$?([0-9,]+\.?[0-9]*)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data[field] = match.group(1).strip()
        
        return data
    
    def process_tax_document(self, file_path: str, document_type: str) -> Dict:
        """Process a tax document and extract relevant data."""
        # Extract text from document
        text = self.extract_text_from_document(file_path)
        
        if not text:
            return {'raw_text': '', 'extracted_data': {}}
        
        # Extract structured data based on document type
        extracted_data = {}
        
        if document_type.lower() == 'w-2':
            extracted_data = self.extract_w2_data(text)
        elif document_type.lower() == '1099':
            extracted_data = self.extract_1099_data(text)
        elif document_type.lower() == 'receipt':
            extracted_data = self.extract_receipt_data(text)
        
        return {
            'raw_text': text,
            'extracted_data': extracted_data
        }
    
    def validate_extracted_data(self, data: Dict, document_type: str) -> List[str]:
        """Validate extracted data and return list of issues."""
        issues = []
        
        if document_type.lower() == 'w-2':
            required_fields = ['employer_name', 'employee_name', 'wages']
            for field in required_fields:
                if not data.get(field):
                    issues.append(f"Missing {field.replace('_', ' ')}")
        
        elif document_type.lower() == '1099':
            required_fields = ['payer_name', 'recipient_name']
            for field in required_fields:
                if not data.get(field):
                    issues.append(f"Missing {field.replace('_', ' ')}")
        
        return issues

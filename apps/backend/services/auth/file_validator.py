import hashlib
import magic
import re
from typing import Tuple, List, Optional
from io import BytesIO
import asyncio
import aiohttp
import logging

logger = logging.getLogger(__name__)

class FileValidator:
    """Service for validating uploaded KYC documents"""
    
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/tiff',
        'image/bmp'
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def calculate_file_hash(file_content: bytes) -> str:
        """Calculate SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    def validate_file_type(file_content: bytes, filename: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate file type using python-magic
        Returns: (is_valid, mime_type, error_message)
        """
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
            
            if mime_type not in FileValidator.ALLOWED_MIME_TYPES:
                return False, mime_type, f"File type not allowed. Allowed types: {', '.join(FileValidator.ALLOWED_MIME_TYPES)}"
            
            # Additional validation for file extension vs MIME type
            file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
            expected_extensions = {
                'application/pdf': ['pdf'],
                'image/jpeg': ['jpg', 'jpeg'],
                'image/png': ['png'],
                'image/tiff': ['tiff', 'tif'],
                'image/bmp': ['bmp']
            }
            
            if mime_type in expected_extensions:
                if file_ext not in expected_extensions[mime_type]:
                    return False, mime_type, f"File extension '{file_ext}' doesn't match MIME type '{mime_type}'"
            
            return True, mime_type, None
            
        except Exception as e:
            logger.error(f"Error validating file type: {e}")
            return False, "unknown", f"Error validating file type: {str(e)}"
    
    @staticmethod
    def validate_file_size(file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validate file size
        Returns: (is_valid, error_message)
        """
        if file_size > FileValidator.MAX_FILE_SIZE:
            return False, f"File size {file_size} bytes exceeds maximum allowed size {FileValidator.MAX_FILE_SIZE} bytes"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, None
    
    @staticmethod
    async def scan_for_viruses(file_content: bytes, filename: str) -> Tuple[str, Optional[str]]:
        """
        Mock virus scanning service
        In production, this would integrate with ClamAV or similar
        Returns: (status, error_message) where status is 'clean', 'infected', or 'error'
        """
        try:
            # Mock virus scanning - in production integrate with ClamAV
            await asyncio.sleep(0.1)  # Simulate scanning time
            
            # Simple heuristic checks for demonstration
            suspicious_patterns = [
                b'<script',
                b'javascript:',
                b'vbscript:',
                b'onload=',
                b'onerror=',
                b'eval(',
                b'document.write'
            ]
            
            file_lower = file_content.lower()
            for pattern in suspicious_patterns:
                if pattern in file_lower:
                    return 'infected', f"Suspicious content detected: {pattern.decode('utf-8', errors='ignore')}"
            
            # Check for executable file signatures
            exe_signatures = [
                b'\x4d\x5a',  # PE executable
                b'\x7f\x45\x4c\x46',  # ELF executable
                b'\xca\xfe\xba\xbe',  # Mach-O executable
            ]
            
            for sig in exe_signatures:
                if file_content.startswith(sig):
                    return 'infected', "Executable file detected"
            
            return 'clean', None
            
        except Exception as e:
            logger.error(f"Error during virus scan: {e}")
            return 'error', f"Virus scan failed: {str(e)}"
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> Optional[str]:
        """
        Extract text from PDF for INN/OGRN validation
        In production, use PyPDF2 or similar library
        """
        try:
            # Mock text extraction - in production use proper PDF parsing
            # This is a simplified version for demonstration
            text_content = file_content.decode('utf-8', errors='ignore')
            return text_content
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None
    
    @staticmethod
    def extract_inn_ogrn_from_text(text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract INN and OGRN numbers from document text
        Returns: (inn, ogrn)
        """
        inn_pattern = r'\b\d{10,12}\b'  # INN is 10 or 12 digits
        ogrn_pattern = r'\b\d{13,15}\b'  # OGRN is 13-15 digits
        
        inn_matches = re.findall(inn_pattern, text)
        ogrn_matches = re.findall(ogrn_pattern, text)
        
        # Simple validation - in production, use more sophisticated extraction
        inn = inn_matches[0] if inn_matches else None
        ogrn = ogrn_matches[0] if ogrn_matches else None
        
        return inn, ogrn
    
    @staticmethod
    async def validate_inn(inn: str) -> Tuple[str, Optional[str]]:
        """
        Validate INN using external API or mock service
        Returns: (status, error_message) where status is 'valid', 'invalid', or 'error'
        """
        try:
            if not inn or len(inn) not in [10, 12]:
                return 'invalid', 'INN must be 10 or 12 digits'
            
            if not inn.isdigit():
                return 'invalid', 'INN must contain only digits'
            
            # Mock validation - in production, integrate with FNS API
            await asyncio.sleep(0.5)  # Simulate API call
            
            # Simple checksum validation for INN
            if len(inn) == 10:
                # Individual INN validation
                coefficients = [2, 4, 10, 3, 5, 9, 4, 6, 8]
                checksum = sum(int(inn[i]) * coefficients[i] for i in range(9)) % 11
                if checksum > 9:
                    checksum = checksum % 10
                
                if checksum != int(inn[9]):
                    return 'invalid', 'Invalid INN checksum'
            
            elif len(inn) == 12:
                # Legal entity INN validation
                coefficients1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
                coefficients2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
                
                checksum1 = sum(int(inn[i]) * coefficients1[i] for i in range(10)) % 11
                if checksum1 > 9:
                    checksum1 = checksum1 % 10
                
                checksum2 = sum(int(inn[i]) * coefficients2[i] for i in range(11)) % 11
                if checksum2 > 9:
                    checksum2 = checksum2 % 10
                
                if checksum1 != int(inn[10]) or checksum2 != int(inn[11]):
                    return 'invalid', 'Invalid INN checksum'
            
            return 'valid', None
            
        except Exception as e:
            logger.error(f"Error validating INN: {e}")
            return 'error', f"INN validation failed: {str(e)}"
    
    @staticmethod
    async def validate_ogrn(ogrn: str) -> Tuple[str, Optional[str]]:
        """
        Validate OGRN using external API or mock service
        Returns: (status, error_message) where status is 'valid', 'invalid', or 'error'
        """
        try:
            if not ogrn or len(ogrn) not in [13, 15]:
                return 'invalid', 'OGRN must be 13 or 15 digits'
            
            if not ogrn.isdigit():
                return 'invalid', 'OGRN must contain only digits'
            
            # Mock validation - in production, integrate with FNS API
            await asyncio.sleep(0.5)  # Simulate API call
            
            # Simple checksum validation for OGRN
            if len(ogrn) == 13:
                # Legal entity OGRN
                checksum = int(ogrn[:12]) % 11
                if checksum > 9:
                    checksum = checksum % 10
                
                if checksum != int(ogrn[12]):
                    return 'invalid', 'Invalid OGRN checksum'
            
            elif len(ogrn) == 15:
                # Individual entrepreneur OGRN
                checksum = int(ogrn[:14]) % 13
                if checksum > 9:
                    checksum = checksum % 10
                
                if checksum != int(ogrn[14]):
                    return 'invalid', 'Invalid OGRN checksum'
            
            return 'valid', None
            
        except Exception as e:
            logger.error(f"Error validating OGRN: {e}")
            return 'error', f"OGRN validation failed: {str(e)}"
    
    @staticmethod
    async def validate_document(
        file_content: bytes, 
        filename: str, 
        document_type: str
    ) -> dict:
        """
        Comprehensive document validation
        Returns validation results dictionary
        """
        results = {
            'file_hash': FileValidator.calculate_file_hash(file_content),
            'file_size': len(file_content),
            'mime_type': None,
            'validation_errors': [],
            'virus_scan_status': 'pending',
            'inn_validation_status': None,
            'ogrn_validation_status': None,
            'extracted_inn': None,
            'extracted_ogrn': None
        }
        
        # Validate file size
        size_valid, size_error = FileValidator.validate_file_size(len(file_content))
        if not size_valid:
            results['validation_errors'].append(size_error)
        
        # Validate file type
        type_valid, mime_type, type_error = FileValidator.validate_file_type(file_content, filename)
        results['mime_type'] = mime_type
        if not type_valid:
            results['validation_errors'].append(type_error)
        
        # Virus scan
        virus_status, virus_error = await FileValidator.scan_for_viruses(file_content, filename)
        results['virus_scan_status'] = virus_status
        if virus_error:
            results['validation_errors'].append(virus_error)
        
        # Extract and validate INN/OGRN for relevant document types
        if document_type in ['inn', 'ogrn', 'business_license'] and mime_type == 'application/pdf':
            text_content = FileValidator.extract_text_from_pdf(file_content)
            if text_content:
                inn, ogrn = FileValidator.extract_inn_ogrn_from_text(text_content)
                results['extracted_inn'] = inn
                results['extracted_ogrn'] = ogrn
                
                if inn:
                    inn_status, inn_error = await FileValidator.validate_inn(inn)
                    results['inn_validation_status'] = inn_status
                    if inn_error:
                        results['validation_errors'].append(f"INN validation: {inn_error}")
                
                if ogrn:
                    ogrn_status, ogrn_error = await FileValidator.validate_ogrn(ogrn)
                    results['ogrn_validation_status'] = ogrn_status
                    if ogrn_error:
                        results['validation_errors'].append(f"OGRN validation: {ogrn_error}")
        
        return results
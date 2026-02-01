"""
Intelligence Extractor for the Agentic Honey-Pot System.
Extracts bank accounts, UPI IDs, phishing URLs, and other scam data.
"""

import re
from typing import List
from models import ExtractedIntelligence


class IntelligenceExtractor:
    """Extracts actionable intelligence from scam conversations."""
    
    def __init__(self):
        # UPI provider suffixes
        self.upi_suffixes = [
            'upi', 'paytm', 'phonepe', 'gpay', 'oksbi', 'okicici',
            'okaxis', 'okhdfcbank', 'ybl', 'ibl', 'axl', 'sbi',
            'icici', 'hdfc', 'axis', 'kotak', 'indus', 'federal',
            'apl', 'pingpay', 'freecharge', 'airtel', 'jio', 'barodampay',
            'mahb', 'citi', 'citigold', 'axisb', 'hdfcbank', 'sbin'
        ]
        
        # Compile regex patterns
        self.ifsc_pattern = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', re.IGNORECASE)
        self.url_pattern = re.compile(r'https?://[^\s<>"\'{}|\\^`\[\]]+', re.IGNORECASE)
        self.phone_pattern = re.compile(r'(?:\+91|91|0)?[6-9]\d{9}\b')
        # More flexible UPI pattern - word@word format
        self.upi_pattern = re.compile(r'\b[a-zA-Z0-9._-]+@[a-zA-Z]+\b')
        # Bank account: 9-18 digits
        self.bank_pattern = re.compile(r'\b\d{9,18}\b')
    
    def extract_from_text(self, text: str) -> ExtractedIntelligence:
        """Extract all intelligence from a text message."""
        
        # Extract URLs first (to avoid matching parts as UPI)
        phishing_urls = self._extract_urls(text)
        
        # Remove URLs from text for other extractions
        text_no_urls = text
        for url in phishing_urls:
            text_no_urls = text_no_urls.replace(url, ' ')
        
        # Extract IFSC codes
        ifsc_codes = [code.upper() for code in self.ifsc_pattern.findall(text)]
        
        # Extract UPI IDs
        upi_ids = self._extract_upi_ids(text_no_urls)
        
        # Extract phone numbers
        phone_numbers = self._extract_phone_numbers(text)
        
        # Extract bank accounts (after removing phone numbers from consideration)
        bank_accounts = self._extract_bank_accounts(text, phone_numbers)
        
        return ExtractedIntelligence(
            bank_accounts=list(set(bank_accounts)),
            ifsc_codes=list(set(ifsc_codes)),
            upi_ids=list(set(upi_ids)),
            phishing_urls=list(set(phishing_urls)),
            phone_numbers=list(set(phone_numbers))
        )
    
    def extract_from_conversation(self, messages: List[dict]) -> ExtractedIntelligence:
        """Extract intelligence from entire conversation history."""
        combined = ExtractedIntelligence()
        
        for msg in messages:
            # Only extract from scammer messages, not agent responses
            if msg.get('role') == 'scammer':
                content = msg.get('content', '')
                extracted = self.extract_from_text(content)
                
                combined.bank_accounts.extend(extracted.bank_accounts)
                combined.ifsc_codes.extend(extracted.ifsc_codes)
                combined.upi_ids.extend(extracted.upi_ids)
                combined.phishing_urls.extend(extracted.phishing_urls)
                combined.phone_numbers.extend(extracted.phone_numbers)
        
        # Deduplicate
        combined.bank_accounts = list(set(combined.bank_accounts))
        combined.ifsc_codes = list(set(combined.ifsc_codes))
        combined.upi_ids = list(set(combined.upi_ids))
        combined.phishing_urls = list(set(combined.phishing_urls))
        combined.phone_numbers = list(set(combined.phone_numbers))
        
        return combined
    
    def _extract_bank_accounts(self, text: str, phone_numbers: List[str]) -> List[str]:
        """Extract bank account numbers (excluding phone numbers)."""
        accounts = []
        matches = self.bank_pattern.findall(text)
        
        for match in matches:
            # Skip if it's a phone number
            is_phone = False
            for phone in phone_numbers:
                if match in phone or phone in match:
                    is_phone = True
                    break
            
            if is_phone:
                continue
                
            # Skip 10-digit numbers starting with 6-9 (likely phone numbers)
            if len(match) == 10 and match[0] in '6789':
                continue
            
            # Valid bank accounts are typically 9-18 digits
            if 9 <= len(match) <= 18:
                accounts.append(match)
        
        return accounts
    
    def _extract_upi_ids(self, text: str) -> List[str]:
        """Extract UPI IDs from text."""
        upi_ids = []
        matches = self.upi_pattern.findall(text.lower())
        
        for match in matches:
            # Check if it looks like a UPI ID (has @ and ends with known suffix)
            if '@' in match:
                # Get the part after @
                suffix = match.split('@')[1]
                
                # Check against known UPI suffixes
                if suffix in self.upi_suffixes:
                    upi_ids.append(match)
                # Also accept if it's short (likely a bank code)
                elif len(suffix) <= 10 and suffix.isalpha():
                    upi_ids.append(match)
        
        return upi_ids
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs (potential phishing links)."""
        urls = self.url_pattern.findall(text)
        cleaned = []
        
        for url in urls:
            # Remove trailing punctuation
            url = url.rstrip('.,;:!?')
            cleaned.append(url)
        
        return cleaned
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract Indian phone numbers."""
        matches = self.phone_pattern.findall(text)
        normalized = []
        
        for match in matches:
            # Normalize: remove country code, keep 10 digits
            number = re.sub(r'^(\+91|91|0)', '', match)
            if len(number) == 10 and number[0] in '6789':
                normalized.append(number)
        
        return normalized


# Singleton instance
intelligence_extractor = IntelligenceExtractor()

"""
Intelligence Extractor for the Agentic Honey-Pot System.
Extracts bank accounts, UPI IDs, phishing URLs, and other scam data.
"""

import re
from typing import Dict, Any, List
from config import config
from models import ExtractedIntelligence


class IntelligenceExtractor:
    """Extracts actionable intelligence from scam conversations."""
    
    def __init__(self):
        self.bank_pattern = re.compile(config.BANK_ACCOUNT_PATTERN)
        self.ifsc_pattern = re.compile(config.IFSC_PATTERN)
        self.upi_pattern = re.compile(config.UPI_PATTERN)
        self.url_pattern = re.compile(config.URL_PATTERN)
        self.phone_pattern = re.compile(config.PHONE_PATTERN)
        
        # UPI provider suffixes to validate UPI IDs
        self.upi_suffixes = [
            '@upi', '@paytm', '@phonepe', '@gpay', '@oksbi', '@okicici',
            '@okaxis', '@okhdfcbank', '@ybl', '@ibl', '@axl', '@sbi',
            '@icici', '@hdfc', '@axis', '@kotak', '@indus', '@federal'
        ]
    
    def extract_from_text(self, text: str) -> ExtractedIntelligence:
        """Extract all intelligence from a text message."""
        text_lower = text.lower()
        
        # Extract bank account numbers (9-18 digits, excluding common non-account numbers)
        bank_accounts = self._extract_bank_accounts(text)
        
        # Extract IFSC codes
        ifsc_codes = self.ifsc_pattern.findall(text.upper())
        
        # Extract UPI IDs
        upi_ids = self._extract_upi_ids(text_lower)
        
        # Extract URLs (potential phishing links)
        phishing_urls = self._extract_urls(text)
        
        # Extract phone numbers
        phone_numbers = self._extract_phone_numbers(text)
        
        return ExtractedIntelligence(
            bank_accounts=list(set(bank_accounts)),
            ifsc_codes=list(set(ifsc_codes)),
            upi_ids=list(set(upi_ids)),
            phishing_urls=list(set(phishing_urls)),
            phone_numbers=list(set(phone_numbers))
        )
    
    def extract_from_conversation(self, messages: List[Dict[str, str]]) -> ExtractedIntelligence:
        """Extract intelligence from entire conversation history."""
        combined = ExtractedIntelligence()
        
        for msg in messages:
            content = msg.get('content', '')
            extracted = self.extract_from_text(content)
            
            # Merge all extracted data
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
    
    def _extract_bank_accounts(self, text: str) -> List[str]:
        """Extract potential bank account numbers."""
        accounts = []
        matches = self.bank_pattern.findall(text)
        
        for match in matches:
            # Filter out common non-account patterns
            # Account numbers are typically 9-18 digits
            if 9 <= len(match) <= 18:
                # Exclude patterns that look like phone numbers (10 digits starting with 6-9)
                if len(match) == 10 and match[0] in '6789':
                    continue
                # Exclude patterns that look like dates or years
                if len(match) == 4 and 1900 <= int(match) <= 2100:
                    continue
                accounts.append(match)
        
        return accounts
    
    def _extract_upi_ids(self, text: str) -> List[str]:
        """Extract UPI IDs from text."""
        upi_ids = []
        potential_matches = self.upi_pattern.findall(text)
        
        for match in potential_matches:
            # Check if it looks like a valid UPI ID
            for suffix in self.upi_suffixes:
                if match.endswith(suffix) or suffix.replace('@', '') in match:
                    upi_ids.append(match)
                    break
            # Also check for generic UPI pattern (something@something)
            if '@' in match and len(match) > 5:
                # Exclude email-like patterns
                if not any(ext in match for ext in ['.com', '.in', '.org', '.net', '.edu']):
                    if match not in upi_ids:
                        upi_ids.append(match)
        
        return upi_ids
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs (potential phishing links)."""
        urls = self.url_pattern.findall(text)
        
        # Filter and clean URLs
        cleaned_urls = []
        for url in urls:
            # Remove trailing punctuation
            url = url.rstrip('.,;:!?')
            cleaned_urls.append(url)
        
        return cleaned_urls
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract Indian phone numbers."""
        matches = self.phone_pattern.findall(text)
        
        # Normalize phone numbers
        normalized = []
        for match in matches:
            # Remove country code prefix
            number = re.sub(r'^(\+91|91|0)', '', match)
            if len(number) == 10:
                normalized.append(number)
        
        return normalized


# Singleton instance
intelligence_extractor = IntelligenceExtractor()

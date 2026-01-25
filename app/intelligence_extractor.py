"""
Intelligence Extraction Module.
Uses regex patterns + AI validation to extract actionable intelligence.
"""

import re
from typing import List, Tuple
from app.models import ExtractedIntelligence


class IntelligenceExtractor:
    """
    Extracts scam-related intelligence from conversations.
    Combines regex pattern matching with contextual validation.
    """
    
    # UPI ID Pattern: username@bankname or phone@upi
    UPI_PATTERN = re.compile(
        r'\b[a-zA-Z0-9._-]+@[a-zA-Z]{2,}[a-zA-Z0-9]*\b',
        re.IGNORECASE
    )
    
    # Indian Bank Account Pattern: 9-18 digits
    BANK_ACCOUNT_PATTERN = re.compile(
        r'\b\d{9,18}\b'
    )
    
    # IFSC Code Pattern: 4 letters + 0 + 6 alphanumeric
    IFSC_PATTERN = re.compile(
        r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
        re.IGNORECASE
    )
    
    # URL/Phishing Link Pattern
    URL_PATTERN = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+|'
        r'www\.[^\s<>"{}|\\^`\[\]]+|'
        r'\b[a-zA-Z0-9][-a-zA-Z0-9]*\.(com|org|net|in|co\.in|xyz|online|site|click|tk|ml|ga|cf|gq|top|info|biz|pw|cc|link|live|shop|store|app|io|me|to|pro)[^\s]*',
        re.IGNORECASE
    )
    
    # Common UPI apps/bank suffixes for validation
    VALID_UPI_SUFFIXES = {
        'ybl', 'okhdfcbank', 'okaxis', 'oksbi', 'okicici',
        'paytm', 'upi', 'gpay', 'ibl', 'axl', 'sbi',
        'icici', 'hdfc', 'axis', 'kotak', 'bob', 'pnb',
        'canara', 'union', 'indian', 'idbi', 'rbl', 'yes',
        'federal', 'indus', 'dbs', 'citi', 'hsbc', 'sc',
        'apl', 'pingpay', 'freecharge', 'airtel', 'jio',
        'waaxis', 'wahdfcbank', 'wasbi', 'waicici'
    }
    
    # Suspicious/phishing domain indicators
    SUSPICIOUS_INDICATORS = [
        'verify', 'secure', 'update', 'confirm', 'login',
        'bank', 'account', 'claim', 'prize', 'winner',
        'kyc', 'suspend', 'block', 'urgent', 'reward',
        'lottery', 'lucky', 'bonus', 'offer', 'free'
    ]
    
    @classmethod
    def extract_all(cls, text: str) -> ExtractedIntelligence:
        """
        Extract all intelligence from the given text.
        
        Args:
            text: The text to analyze (can be full conversation)
            
        Returns:
            ExtractedIntelligence object with all findings
        """
        upi_ids = cls._extract_upi_ids(text)
        bank_accounts, ifsc_codes = cls._extract_bank_info(text)
        phishing_links = cls._extract_phishing_links(text)
        
        # Combine bank accounts with IFSC codes
        bank_info = list(set(bank_accounts))
        if ifsc_codes:
            for ifsc in ifsc_codes:
                bank_info.append(f"IFSC: {ifsc}")
        
        return ExtractedIntelligence(
            bankAccounts=bank_info[:10],  # Limit to 10
            upiIds=list(set(upi_ids))[:10],
            phishingLinks=list(set(phishing_links))[:10]
        )
    
    @classmethod
    def _extract_upi_ids(cls, text: str) -> List[str]:
        """Extract and validate UPI IDs."""
        candidates = cls.UPI_PATTERN.findall(text)
        valid_upis = []
        
        # Filter out email-like patterns and validate UPI format
        for candidate in candidates:
            # Skip if it looks like a regular email
            if cls._is_likely_email(candidate):
                continue
            
            # Check if suffix matches known UPI providers
            suffix = candidate.split('@')[-1].lower()
            if suffix in cls.VALID_UPI_SUFFIXES or 'upi' in suffix or 'pay' in suffix:
                valid_upis.append(candidate)
            # Also accept if it has typical UPI patterns
            elif re.match(r'^\d{10}@', candidate):  # Phone number based UPI
                valid_upis.append(candidate)
        
        return valid_upis
    
    @classmethod
    def _is_likely_email(cls, text: str) -> bool:
        """Check if the text is likely an email rather than UPI ID."""
        email_domains = ['gmail', 'yahoo', 'hotmail', 'outlook', 'mail', 'email']
        suffix = text.split('@')[-1].lower()
        return any(domain in suffix for domain in email_domains)
    
    @classmethod
    def _extract_bank_info(cls, text: str) -> Tuple[List[str], List[str]]:
        """Extract bank account numbers and IFSC codes."""
        # Find potential account numbers
        account_candidates = cls.BANK_ACCOUNT_PATTERN.findall(text)
        
        # Filter out unlikely account numbers (phone numbers, etc.)
        valid_accounts = []
        for acc in account_candidates:
            # Skip if it looks like a phone number (10 digits starting with 6-9)
            if len(acc) == 10 and acc[0] in '6789':
                continue
            # Skip if it's a common non-account pattern
            if len(acc) < 9 or len(acc) > 18:
                continue
            # Context check: is "account" or "a/c" nearby?
            if cls._has_bank_context(text, acc):
                valid_accounts.append(acc)
        
        # Find IFSC codes
        ifsc_codes = cls.IFSC_PATTERN.findall(text)
        
        return valid_accounts, ifsc_codes
    
    @classmethod
    def _has_bank_context(cls, text: str, number: str) -> bool:
        """Check if a number appears in bank-related context."""
        # Find the position of the number
        pos = text.find(number)
        if pos == -1:
            return True  # If we can't find position, include it
        
        # Get surrounding context (100 chars before and after)
        start = max(0, pos - 100)
        end = min(len(text), pos + len(number) + 100)
        context = text[start:end].lower()
        
        bank_keywords = [
            'account', 'a/c', 'bank', 'transfer', 'send', 'money',
            'deposit', 'credit', 'debit', 'neft', 'rtgs', 'imps',
            'ifsc', 'branch', 'savings', 'current'
        ]
        
        return any(keyword in context for keyword in bank_keywords)
    
    @classmethod
    def _extract_phishing_links(cls, text: str) -> List[str]:
        """Extract and validate suspicious/phishing links."""
        # More comprehensive URL pattern
        url_pattern = re.compile(
            r'https?://[^\s<>"\'{}|\\^`\[\]]+|'
            r'www\.[^\s<>"\'{}|\\^`\[\]]+',
            re.IGNORECASE
        )
        
        urls = url_pattern.findall(text)
        suspicious_urls = []
        
        for url in urls:
            url = url.strip('.,;:!?()')
            url_lower = url.lower()
            
            # Skip legitimate domains
            if cls._is_legitimate_domain(url_lower):
                continue
            
            # Check for suspicious patterns
            is_suspicious = any(indicator in url_lower for indicator in cls.SUSPICIOUS_INDICATORS)
            
            # Check for URL shorteners
            shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'is.gd', 'buff.ly']
            is_shortened = any(shortener in url_lower for shortener in shorteners)
            
            # Check for suspicious TLDs
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.click', '.online', '.site', '.win', '.vip']
            has_suspicious_tld = any(tld in url_lower for tld in suspicious_tlds)
            
            # Any non-legitimate URL in a scam context should be flagged
            if is_suspicious or is_shortened or has_suspicious_tld:
                suspicious_urls.append(url)
        
        return suspicious_urls
    
    @classmethod
    def _is_legitimate_domain(cls, url: str) -> bool:
        """Check if URL belongs to a legitimate domain."""
        legitimate_domains = [
            'google.com', 'facebook.com', 'twitter.com', 'instagram.com',
            'youtube.com', 'github.com', 'linkedin.com', 'microsoft.com',
            'apple.com', 'amazon.com', 'wikipedia.org', 'gov.in',
            'sbi.co.in', 'hdfcbank.com', 'icicibank.com', 'axisbank.com'
        ]
        return any(domain in url for domain in legitimate_domains)
    
    @classmethod
    def extract_from_conversation(cls, messages: List[dict]) -> ExtractedIntelligence:
        """
        Extract intelligence from entire conversation history.
        
        Args:
            messages: List of message dicts with 'text' field
            
        Returns:
            Combined ExtractedIntelligence from all messages
        """
        all_text = " ".join(msg.get('text', '') for msg in messages)
        return cls.extract_all(all_text)

"""
Configuration module for the Agentic Honey-Pot System.
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration settings."""
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    HONEYPOT_API_KEY: str = os.getenv("HONEYPOT_API_KEY", "test-key-123")
    
    # Groq Model Configuration
    GROQ_MODEL: str = "llama-3.1-8b-instant"  # Fast, free model
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Agent Persona Configuration
    AGENT_PERSONA = {
        "name": "Ramesh Kumar",
        "age": "58",
        "occupation": "Retired government employee",
        "location": "Lucknow",
        "characteristics": [
            "Trusting and naive about technology",
            "Eager to receive money or prizes",
            "Slightly confused but cooperative",
            "Asks clarifying questions",
            "Takes time to understand instructions"
        ]
    }
    
    # Scam Detection Keywords (weighted)
    SCAM_KEYWORDS = {
        "high_confidence": [
            "lottery", "won", "prize", "winner", "congratulations",
            "lakhs", "crores", "claim", "reward", "lucky",
            "bank account", "account number", "ifsc", "upi",
            "otp", "pin", "password", "cvv", "card number",
            "kyc", "verification", "blocked", "suspended",
            "urgent", "immediately", "expire", "deadline"
        ],
        "medium_confidence": [
            "transfer", "payment", "amount", "rupees", "rs",
            "click", "link", "download", "install", "app",
            "customer care", "support", "helpline", "toll-free",
            "refund", "cashback", "bonus", "offer", "discount"
        ]
    }
    
    # Intelligence Extraction Patterns
    BANK_ACCOUNT_PATTERN = r'\b\d{9,18}\b'
    IFSC_PATTERN = r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
    UPI_PATTERN = r'\b[\w.-]+@[\w]+\b'
    URL_PATTERN = r'https?://[^\s<>"{}|\\^`\[\]]+'
    PHONE_PATTERN = r'\b(?:\+91|91|0)?[6-9]\d{9}\b'


config = Config()

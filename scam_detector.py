"""
Scam Detector for the Agentic Honey-Pot System.
Detects scam intent using keyword analysis and AI-powered analysis.
"""

from typing import Tuple, List, Dict
from groq import Groq
from config import config


class ScamDetector:
    """Detects scam intent in messages using multi-layered analysis."""
    
    def __init__(self):
        self.high_confidence_keywords = config.SCAM_KEYWORDS["high_confidence"]
        self.medium_confidence_keywords = config.SCAM_KEYWORDS["medium_confidence"]
        self.groq_client = None
        self._init_groq()
    
    def _init_groq(self):
        """Initialize Groq API for advanced scam detection."""
        if config.GROQ_API_KEY:
            try:
                self.groq_client = Groq(api_key=config.GROQ_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize Groq API: {e}")
                self.groq_client = None
    
    def detect(self, message: str, conversation_history: List[Dict[str, str]] = None) -> Tuple[bool, float, str]:
        """
        Detect if a message indicates scam intent.
        
        Returns:
            Tuple of (is_scam: bool, confidence: float, reason: str)
        """
        message_lower = message.lower()
        
        # Layer 1: Keyword-based detection
        keyword_score, keyword_matches = self._keyword_analysis(message_lower)
        
        # Layer 2: Pattern-based detection
        pattern_score = self._pattern_analysis(message)
        
        # Layer 3: AI-based detection (if available)
        ai_score, ai_reason = self._ai_analysis(message, conversation_history)
        
        # Combine scores with weights
        combined_score = (
            keyword_score * 0.35 +
            pattern_score * 0.25 +
            ai_score * 0.40
        )
        
        # Normalize to 0-1
        confidence = min(combined_score, 1.0)
        
        # Determine if scam based on threshold
        is_scam = confidence >= 0.45
        
        # Generate reason
        if keyword_matches:
            reason = f"Scam keywords detected: {', '.join(keyword_matches[:3])}"
        elif ai_reason:
            reason = ai_reason
        else:
            reason = "Pattern analysis indicates potential scam"
        
        return is_scam, confidence, reason
    
    def _keyword_analysis(self, message_lower: str) -> Tuple[float, List[str]]:
        """Analyze message for scam keywords."""
        score = 0.0
        matches = []
        
        for keyword in self.high_confidence_keywords:
            if keyword in message_lower:
                score += 0.3
                matches.append(keyword)
        
        for keyword in self.medium_confidence_keywords:
            if keyword in message_lower:
                score += 0.15
                matches.append(keyword)
        
        return min(score, 1.0), matches
    
    def _pattern_analysis(self, message: str) -> float:
        """Analyze message patterns indicative of scams."""
        score = 0.0
        
        urgency_patterns = ['!!!', 'URGENT', 'IMMEDIATELY', 'NOW', 'TODAY ONLY', 'LIMITED TIME']
        for pattern in urgency_patterns:
            if pattern in message.upper():
                score += 0.2
        
        import re
        money_pattern = r'(Rs\.?|₹|INR)\s*[\d,.]+'
        if re.search(money_pattern, message, re.IGNORECASE):
            score += 0.25
        
        large_amounts = ['lakh', 'crore', 'million']
        for amount in large_amounts:
            if amount in message.lower():
                score += 0.3
        
        sensitive_requests = ['send your', 'share your', 'provide your', 'give me your']
        for req in sensitive_requests:
            if req in message.lower():
                score += 0.25
        
        return min(score, 1.0)
    
    def _ai_analysis(self, message: str, conversation_history: List[Dict[str, str]] = None) -> Tuple[float, str]:
        """Use Groq AI for advanced scam detection."""
        if not self.groq_client:
            return 0.5, ""
        
        try:
            context = ""
            if conversation_history:
                recent_messages = conversation_history[-5:]
                context = "Conversation history:\n"
                for msg in recent_messages:
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    context += f"{role}: {content}\n"
            
            prompt = f"""Analyze if the following message is part of a scam attempt. 
Common scam types in India include: lottery scams, KYC fraud, OTP fraud, job scams, 
loan scams, investment fraud, and impersonation of bank officials.

{context}

Latest message to analyze: "{message}"

Respond with ONLY a JSON object in this exact format (no markdown):
{{"is_scam": true, "confidence": 0.85, "reason": "brief explanation"}}"""

            response = self.groq_client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            
            response_text = response.choices[0].message.content.strip()
            
            import json
            if response_text.startswith('```'):
                response_text = response_text.split('\n', 1)[1]
                response_text = response_text.rsplit('```', 1)[0]
            
            result = json.loads(response_text)
            score = result.get('confidence', 0.5)
            reason = result.get('reason', '')
            
            return score, reason
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return 0.5, ""


scam_detector = ScamDetector()

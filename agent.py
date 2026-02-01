"""
Autonomous AI Agent for the Agentic Honey-Pot System.
Engages scammers with a believable human persona to extract intelligence.
"""

from groq import Groq
from typing import List, Dict
from config import config


class HoneypotAgent:
    """
    Autonomous AI agent that maintains a believable human persona
    and engages scammers to extract intelligence.
    """
    
    def __init__(self):
        self.persona = config.AGENT_PERSONA
        self.groq_client = None
        self._init_groq()
    
    def _init_groq(self):
        """Initialize Groq client for response generation."""
        if config.GROQ_API_KEY:
            try:
                self.groq_client = Groq(api_key=config.GROQ_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize Groq for agent: {e}")
                self.groq_client = None
    
    def generate_response(
        self, 
        scammer_message: str, 
        conversation_history: List[Dict[str, str]],
        scam_detected: bool = False
    ) -> str:
        """Generate a response to the scammer's message."""
        if self.groq_client:
            return self._generate_ai_response(scammer_message, conversation_history, scam_detected)
        else:
            return self._generate_fallback_response(scammer_message, scam_detected)
    
    def _generate_ai_response(
        self, 
        scammer_message: str, 
        conversation_history: List[Dict[str, str]],
        scam_detected: bool
    ) -> str:
        """Generate response using Groq AI."""
        
        history_text = ""
        for msg in conversation_history[-8:]:
            role = "Scammer" if msg["role"] == "scammer" else "Me"
            history_text += f"{role}: {msg['content']}\n"
        
        persona = self.persona
        characteristics = "\n".join(f"- {c}" for c in persona["characteristics"])
        
        if scam_detected:
            strategy = """
STRATEGIC OBJECTIVES (hidden from response):
1. Keep the conversation going to extract more information
2. Ask for specific details like bank account, UPI ID, or payment links
3. Show interest but appear slightly confused to make scammer explain more
4. Ask clarifying questions about how to send money or claim prizes
5. Request the scammer to repeat or confirm sensitive details
6. NEVER reveal that you know this is a scam
7. Act increasingly trusting and eager to comply
"""
        else:
            strategy = """
OBJECTIVES:
1. Respond naturally as the persona would
2. Show appropriate level of interest based on the message
3. Be polite and conversational
"""
        
        system_prompt = f"""You are roleplaying as {persona['name']}, a {persona['age']}-year-old {persona['occupation']} from {persona['location']}.

PERSONA CHARACTERISTICS:
{characteristics}

{strategy}

RULES:
- Keep responses natural, 1-3 sentences
- Use simple Hindi-English mix if appropriate
- DO NOT reveal you know this is a scam
- DO NOT add any system notes or explanations
- Just provide the direct response"""

        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        for msg in conversation_history[-6:]:
            role = "user" if msg["role"] == "scammer" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
        
        # Add latest message
        messages.append({"role": "user", "content": scammer_message})

        try:
            response = self.groq_client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI response generation error: {e}")
            return self._generate_fallback_response(scammer_message, scam_detected)
    
    def _generate_fallback_response(self, scammer_message: str, scam_detected: bool) -> str:
        """Generate a fallback response when AI is unavailable."""
        message_lower = scammer_message.lower()
        
        if scam_detected:
            if any(word in message_lower for word in ['account', 'bank', 'transfer']):
                return "Ji haan, I want to receive the money. Which bank account should I give? Please tell me what details you need."
            elif any(word in message_lower for word in ['upi', 'paytm', 'phonepe', 'gpay']):
                return "I have UPI. Should I send you my UPI ID? Or do you have a UPI ID where I should send?"
            elif any(word in message_lower for word in ['link', 'click', 'website']):
                return "Please send the link again, I could not see properly. My phone is little old, sometimes links don't open."
            elif any(word in message_lower for word in ['otp', 'code', 'verification']):
                return "OTP? You mean the number that comes on phone? Yes yes, I can share. What should I do?"
            elif any(word in message_lower for word in ['lottery', 'prize', 'won', 'winner']):
                return "Really? I won? This is so wonderful! How much is the prize? How do I claim it?"
            elif any(word in message_lower for word in ['kyc', 'verify', 'update']):
                return "Yes, I need to do KYC. Please guide me step by step, I am not very good with phones."
            else:
                return "Ji, I am interested. Please tell me more details. What should I do next?"
        else:
            if any(word in message_lower for word in ['hello', 'hi', 'namaste']):
                return "Namaste ji, kaun bol raha hai?"
            elif '?' in scammer_message:
                return "Ji haan, please tell me more."
            else:
                return "Achha ji, please continue."


honeypot_agent = HoneypotAgent()
